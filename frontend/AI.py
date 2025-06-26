from transformers import pipeline

# Initialize once when the app starts
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_titles(titles: list[str]) -> str:
    try:
        """Generate a thematic summary from a list of article titles."""
        if not titles:
            return "No titles to summarize."
        
        combined_text = " ".join(titles)
        summary = summarizer(
            combined_text,
            max_length=100,
            min_length=30,
            do_sample=False
        )
        return summary[0]['summary_text']

    except Exception as e:
        print('something went wrong with the API', e)