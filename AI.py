# from flask import Flask, request, jsonify
# from transformers import pipeline
# from functools import lru_cache
# import logging
# import time
# import os
# from collections import Counter
# import re
# import torch  # Added missing import

# app = Flask(__name__)
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Initialize summarizer
# _summarizer_instance = None
# _model_load_attempted = False

# def get_summarizer():
#     """Initialize summarizer with PyTorch-first approach"""
#     global _summarizer_instance, _model_load_attempted
    
#     if _summarizer_instance is None and not _model_load_attempted:
#         _model_load_attempted = True
        
#         models = [
#             "sshleifer/distilbart-cnn-12-6",
#             "t5-small",
#             "facebook/bart-large-cnn"
#         ]
        
#         device = 0 if os.getenv("USE_GPU", "0") == "1" and torch.cuda.is_available() else -1
#         logger.info(f"Using device: {'GPU' if device == 0 else 'CPU'}")
        
#         for model_name in models:
#             try:
#                 logger.info(f"Attempting to load: {model_name}")
#                 _summarizer_instance = pipeline(
#                     "summarization",
#                     model=model_name,
#                     framework="pt",
#                     device=device
#                 )
#                 logger.info(f"Successfully loaded {model_name}")
#                 break
#             except Exception as e:
#                 logger.warning(f"Failed to load {model_name}: {str(e)}")
#                 continue
                
#         if _summarizer_instance is None:
#             logger.error("All model loading attempts failed")
            
#     return _summarizer_instance

# @lru_cache(maxsize=32)
# def summarize_titles(titles_tuple: tuple) -> str:
#     """Generate summary with robust fallbacks"""
#     try:
#         logger.debug(f"Processing {len(titles_tuple)} titles")
#         summarizer = get_summarizer()
#         if summarizer:
#             # Join titles, limit each to 200 chars, total to 4000 chars
#             text = ". ".join(str(t).strip()[:200] for t in titles_tuple if t)[:4000]
#             if text:
#                 result = summarizer(
#                     text,
#                     max_length=100,
#                     min_length=30,
#                     do_sample=False,
#                     truncation=True
#                 )
#                 summary = result[0]['summary_text'].strip()
#                 logger.debug(f"Generated summary: {summary}")
#                 return summary
        
#         # Fallback if models fail
#         return _simple_summary(titles_tuple)
        
#     except Exception as e:
#         logger.error(f"Summarization error: {str(e)}", exc_info=True)
#         return _simple_summary(titles_tuple)

# def _simple_summary(titles):
#     """Basic fallback summary using keyword extraction"""
#     try:
#         valid = [str(t).strip() for t in titles if t]
#         if not valid:
#             return "No titles available"
        
#         combined_text = " ".join(valid).lower()
#         words = re.findall(r'\b\w+\b', combined_text)
#         stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'not'}
#         filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
#         word_freq = Counter(filtered_words)
#         top_words = [word for word, _ in word_freq.most_common(3)]
        
#         if top_words:
#             return f"Summary: Articles focus on {', '.join(top_words)}."
#         return "Top stories: " + "; ".join(t[:100] for t in valid[:3])
#     except Exception as e:
#         logger.error(f"Fallback summary error: {str(e)}")
#         return "Summary not available"

# @app.route("/get_summary", methods=["GET"])
# def get_articles_summary():
#     """Endpoint for article summaries"""
#     start_time = time.time()
    
#     try:
#         params = {
#             'and_keywords': [kw for kw in request.args.getlist("and") if kw],
#             'or_keywords': [kw for kw in request.args.getlist("or") if kw],
#             'not_keywords': [kw for kw in request.args.getlist("not") if kw],
#             'sources': [s for s in request.args.getlist("source") if s]
#         }
        
#         logger.debug(f"Query parameters: {params}")

#         if not any(params.values()):
#             return jsonify({
#                 "error": "At least one query parameter (and, or, not, source) is required"
#             }), 400

#         # Build WHERE clause (implementation assumed elsewhere)
#         where_clause, query_params = build_where_clause(
#             params['and_keywords'],
#             params['or_keywords'],
#             params['not_keywords'],
#             params['sources']
#         )

#         # Fetch titles
#         with get_db_connection() as conn, conn.cursor() as cursor:
#             cursor.execute(f"""
#                 SELECT title FROM articles
#                 WHERE {where_clause}
#                 ORDER BY date DESC
#                 LIMIT 20;
#             """, query_params)
#             titles = [row[0] for row in cursor.fetchall()]
        
#         logger.debug(f"Fetched {len(titles)} titles")

#         response = {
#             "count": len(titles),
#             "processing_time_ms": round((time.time() - start_time) * 1000, 2)
#         }

#         if not titles:
#             response["summary"] = "No matching articles found"
#             return jsonify(response), 200

#         if len(titles) < 3:
#             response.update({
#                 "summary": "Insufficient data for full summary",
#                 "titles": titles
#             })
#             return jsonify(response), 200

#         # Generate summary - KEY FIX: Ensure we pass a tuple
#         try:
#             titles_to_summarize = tuple(titles[:15])  # Convert to tuple for lru_cache
#             response["summary"] = summarize_titles(titles_to_summarize)
#             response["titles"] = titles[:5]
#         except Exception as e:
#             logger.warning(f"Summary generation failed: {str(e)}", exc_info=True)
#             response.update({
#                 "summary": _simple_summary(titles[:15]),
#                 "titles": titles[:5],
#                 "warning": "Used fallback summary"
#             })

#         return jsonify(response), 200

#     except Exception as e:
#         logger.error(f"Error in /get_summary: {str(e)}", exc_info=True)
#         return jsonify({
#             "error": "Internal server error",
#             "details": str(e)
#         }), 500

# # Initialize summarizer on import
# try:
#     get_summarizer()
# except Exception as e:
#     logger.error(f"Initial model loading failed: {str(e)}")

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from transformers import pipeline
from functools import lru_cache
import logging
import time
import os
from collections import Counter
import re
import torch

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Summarizer Setup ---
class SummarizerService:
    _instance = None
    _model_load_attempted = False

    def __new__(cls):
        if cls._instance is None and not cls._model_load_attempted:
            cls._model_load_attempted = True
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.models = [
            "sshleifer/distilbart-cnn-12-6",
            "t5-small",
            "facebook/bart-large-cnn"
        ]
        self.device = 0 if os.getenv("USE_GPU", "0") == "1" and torch.cuda.is_available() else -1
        self.summarizer = self._load_model()

    def _load_model(self):
        for model_name in self.models:
            try:
                logger.info(f"Loading model: {model_name}")
                return pipeline(
                    "summarization",
                    model=model_name,
                    framework="pt",
                    device=self.device
                )
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {str(e)}")
        logger.error("All model loading attempts failed")
        return None

# --- Summary Generation ---
class SummaryGenerator:
    def __init__(self):
        self.summarizer_service = SummarizerService()

    @lru_cache(maxsize=32)
    def summarize(self, titles_tuple: tuple) -> str:
        """Generate summary from titles with caching"""
        try:
            if not titles_tuple:
                return "No titles provided"

            # Convert tuple back to list for processing
            titles = list(titles_tuple)
            
            # Try transformer model first
            if self.summarizer_service.summarizer:
                text = self._prepare_text(titles)
                if text:
                    result = self.summarizer_service.summarizer(
                        text,
                        max_length=100,
                        min_length=30,
                        do_sample=False,
                        truncation=True
                    )
                    return result[0]['summary_text'].strip()

            # Fallback to simple summary
            return self._simple_summary(titles)

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}", exc_info=True)
            return self._simple_summary(titles)

    def _prepare_text(self, titles):
        """Prepare text for summarization"""
        return ". ".join(str(t).strip()[:200] for t in titles if t)[:4000]

    def _simple_summary(self, titles):
        """Basic keyword-based fallback"""
        try:
            valid_titles = [str(t).strip() for t in titles if t]
            if not valid_titles:
                return "No titles available"

            words = re.findall(r'\b\w{4,}\b', " ".join(valid_titles).lower())
            stop_words = {'this', 'that', 'with', 'from', 'have', 'has', 'was', 'were'}
            filtered = [w for w in words if w not in stop_words]
            
            if not filtered:
                return "Top stories: " + "; ".join(t[:100] for t in valid_titles[:3])
                
            top_words = Counter(filtered).most_common(3)
            return f"Key topics: {', '.join(w[0] for w in top_words)}"
        except Exception:
            return "Summary not available"