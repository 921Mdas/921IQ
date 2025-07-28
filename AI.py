
import os
import re
import logging
import torch
from functools import lru_cache
from collections import Counter
from typing import List, Tuple, Optional
from transformers import pipeline

logger = logging.getLogger(__name__)

class AIService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__class__._initialized:
            self.__class__._initialized = True
            self.summarizer = self._initialize_summarizer()
            logger.info("✅ AIService initialized")

    def _initialize_summarizer(self) -> Optional[pipeline]:
        """Load summarization model with fallback options"""
        models = [
            "sshleifer/distilbart-cnn-12-6",  # Primary (fastest)
            "facebook/bart-large-cnn",         # Fallback (better quality)
            "t5-small"                          # Lightweight fallback
        ]
        
        device = self._get_device()
        logger.info(f"Using device: {device}")
        
        for model_name in models:
            try:
                logger.info(f"🚀 Attempting to load model: {model_name}")
                summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    framework="pt",
                    device=device
                )
                # Quick test inference to verify model works
                test_result = summarizer("Test", max_length=10, min_length=3)
                logger.info(f"✅ Successfully loaded {model_name}")
                return summarizer
            except Exception as e:
                logger.warning(f"⚠️ Failed to load {model_name}: {e}")
        
        logger.error("All model loading attempts failed")
        return None

    def _get_device(self) -> int:
        """Detect device with more detailed logging"""
        use_gpu = os.getenv("USE_GPU", "0") == "1"
        
        if use_gpu and torch.cuda.is_available():
            logger.info(f"Using CUDA GPU (device 0), {torch.cuda.get_device_name(0)}")
            return 0
        elif use_gpu and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            logger.info("Using MPS (Apple GPU) for inference")
            return "mps"
        
        logger.info("Using CPU for inference")
        return -1

    @lru_cache(maxsize=128)
    def summarize(self, titles: Tuple[str, ...]) -> str:
        """Summarize titles with optimized parameters"""
        try:
            if not titles:
                return "No titles provided"

            titles = titles[:8]
            input_text = self._prepare_text(titles)

            if self.summarizer:
                result = self.summarizer(
                    input_text,
                    max_length=100,
                    min_length=30,
                    do_sample=False,
                    truncation=True,
                    no_repeat_ngram_size=3
                )
                return result[0]["summary_text"].strip()

            return self._simple_summary(titles)

        except Exception as e:
            logger.error(f"Summarization failed: {e}", exc_info=True)
            return self._simple_summary(titles)

    def _prepare_text(self, titles: Tuple[str]) -> str:
        """Merge titles with better text preparation"""
        sanitized = [
            re.sub(r'\s+', ' ', t).strip()[:250]
            for t in titles if t and isinstance(t, str)
        ]
        return ". ".join(sanitized)[:1500]

    def _simple_summary(self, titles: Tuple[str]) -> str:
        """Improved keyword-based fallback summary with French support"""
        try:
            text = " ".join(t for t in titles if isinstance(t, str)).lower()
            words = re.findall(r'\b\w{3,}\b', text)
            
            # Combined English and French stopwords
            stop_words = {
                # English
                "this", "that", "with", "from", "have", "has", "was", "were",
                "their", "they", "them", "these", "those", "will", "would",
                "when", "what", "which", "about", "your", "more", "most",
                "are", "and", "the", "for", "not", "but", "his", "her",
                
                # French
                "le", "la", "les", "de", "des", "du", "un", "une", "et", 
                "ou", "mais", "donc", "or", "ni", "car", "à", "au", "aux",
                "en", "pour", "dans", "sur", "avec", "sans", "sous", "chez",
                "par", "entre", "contre", "dont", "où", "y", "quoi", "qui",
                "que", "qu", "quelle", "quelles", "quels", "quel", "lors",
                "depuis", "pendant", "jusque", "contre", "selon", "après",
                "avant", "contre", "vers", "parmi", "sauf", "voici", "voilà",
                "mon", "ton", "son", "notre", "votre", "leur", "ce", "cet",
                "cette", "ces", "on", "nous", "vous", "ils", "elles", "je",
                "tu", "il", "elle", "se", "me", "te", "ne", "pas", "plus",
                "moins", "comme", "si", "tout", "tous", "toutes", "très",
                "bien", "mal", "peu", "beaucoup", "aussi", "alors", "encore",
                "déjà", "non", "oui", "sont", "été", "être", "avoir", "faire"
            }
            
            filtered = [w for w in words if w not in stop_words and not w.isdigit()]
            top_keywords = Counter(filtered).most_common(4)
            
            if not top_keywords:
                return "Top stories: " + "; ".join(t[:120] for t in titles[:3])
                
            return f"Key topics: {', '.join(w for w, _ in top_keywords)}"
        except Exception as e:
            logger.error(f"Fallback summarizer failed: {e}")
            return "Summary currently unavailable"