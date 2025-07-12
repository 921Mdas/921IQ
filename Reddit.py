# RedditScraper.py
import os
from dotenv import load_dotenv
import praw
from datetime import datetime
from ArticleDB import runDB

load_dotenv()

# Reddit API setup
reddit = praw.Reddit(
    client_id=os.getenv("reddit_id"),
    client_secret=os.getenv("reddit_secret"),
    user_agent="Echo by 921IQ"
)

def reddit_to_article(post):
    return {
        'title': post.title,
        'url': f"https://www.reddit.com{post.permalink}",
        'date': datetime.utcfromtimestamp(post.created_utc),
        'source_name': "Reddit",
        'source_logo': "https://www.redditstatic.com/icon.png",
        'author': post.author.name if post.author else "unknown",
        'category': post.subreddit.display_name,
        'body_intro': (post.selftext or post.title)[:300],
        'named_entities': [],
        'first_comment': "unknown",
        'ad_slots': [],
        'country': "global",
        'reach': post.score,
        'sentiment': "neutral"
    }

def RedditScrap():
    try:
        articles = []
        for post in reddit.subreddit("all").hot(limit=10):
            articles.append(reddit_to_article(post))

        if articles:
            runDB(articles)

        print("✅ Reddit scraping completed.")

    except Exception as e:
        print("❌ in Reddit: Reddit scraping failed:")
        print(e)
