from transformers import pipeline
from functools import lru_cache

_summarizer_instance = None

def get_summarizer():
    global _summarizer_instance
    if _summarizer_instance is None:
        # Use a faster, lighter alternative model if needed:
        # _summarizer_instance = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        _summarizer_instance = pipeline("summarization", model="facebook/bart-large-cnn")
    return _summarizer_instance

def preprocess_titles(titles: list[str]) -> str:
    """Clean and combine titles into a single string."""
    return ". ".join(title.strip() for title in titles if title.strip())

@lru_cache(maxsize=128)
def cached_summarize_titles(titles_tuple: tuple[str]) -> str:
    """Cached version to avoid reprocessing duplicate queries."""
    return summarize_titles(list(titles_tuple))

def summarize_titles(titles: list[str]) -> str:
    """Generate a thematic summary from a list of article titles."""
    try:
        if not titles:
            return "No titles to summarize."

        text = preprocess_titles(titles)
        summarizer = get_summarizer()

        summary = summarizer(
            text,
            max_length=100,
            min_length=30,
            do_sample=False
        )
        return summary[0]['summary_text']
    except Exception as e:
        print("Summarization error:", e)
        return "Failed to generate summary."


