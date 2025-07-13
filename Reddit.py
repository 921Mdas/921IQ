import os
from dotenv import load_dotenv
import praw
from datetime import datetime
from ArticleDB import runDB
from typing import Dict, Any

load_dotenv()

# Reddit API setup
reddit = praw.Reddit(
    client_id=os.getenv("reddit_id"),
    client_secret=os.getenv("reddit_secret"),
    user_agent="Echo by 921IQ"
)

def truncate(text: str, max_length: int) -> str:
    """Safely truncate text to specified length"""
    return text[:max_length] if text else text

def reddit_to_article(post) -> Dict[str, Any]:
    """Convert Reddit post to article dictionary with length validation"""
    first_comment = "unknown"
    try:
        if post.comments:
            first_comment = truncate(post.comments[0].body, 500)
    except Exception:
        pass

    return {
        'title': truncate(post.title, 300),
        'url': truncate(f"https://www.reddit.com{post.permalink}", 500),
        'date': datetime.utcfromtimestamp(post.created_utc),
        'source_name': "Reddit",
        'source_logo': "https://www.redditstatic.com/icon.png",
        'author': truncate(post.author.name if post.author else "unknown", 100),
        'category': truncate(post.subreddit.display_name, 100),
        'body_intro': truncate((post.selftext or post.title), 500),
        'named_entities': [],
        'first_comment': first_comment,
        'ad_slots': [],
        'country': "global",
        'reach': post.score,
        'sentiment': "neutral"
    }

def RedditScrap():
    try:
        print("🔄 Starting Reddit scraping...")
        articles = []
        
        # Get hot posts from multiple categories
        for post in reddit.subreddit("worldnews+news+technology").hot(limit=15):
            articles.append(reddit_to_article(post))

        if articles:
            print(f"📊 Found {len(articles)} Reddit posts")
            runDB(articles)
            print("✅ Reddit scraping completed successfully")
        else:
            print("⚠️ No Reddit posts found")

    except praw.exceptions.PRAWException as e:
        print(f"🔴 PRAW Error: {str(e)}")
    except Exception as e:
        print("❌ Reddit scraping failed:")
        print(f"Error: {str(e)}")