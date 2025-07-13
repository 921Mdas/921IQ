# article_cache.py
import asyncio
from typing import Optional
import aiohttp
import cachetools

class ArticleCache:
    _instance = None
    _cache = cachetools.TTLCache(maxsize=10000, ttl=86400)  # 24 hour cache
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def check_exists(cls, url: str) -> bool:
        """Check if article URL exists in cache"""
        return url in cls._cache
    
    @classmethod
    async def add_article(cls, url: str, data: Optional[dict] = None) -> None:
        """Add article URL to cache"""
        cls._cache[url] = data or {}
    
    @classmethod
    async def clear_cache(cls) -> None:
        """Clear the entire cache"""
        cls._cache.clear()