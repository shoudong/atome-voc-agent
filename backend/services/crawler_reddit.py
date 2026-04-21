"""Reddit crawler using public search.json API (no key needed)."""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx

from backend.database import async_session
from backend.models.post import Post
from backend.services.dedup import is_official_account, is_too_short, mentions_brand
from backend.services.llm_annotator import annotate_unannotated_posts
from backend.services.clustering import cluster_posts
from backend.services.alerting import check_and_send_alerts
from backend.config import settings

from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "PHCreditCards",
    "Philippines",
    "phinvest",
    "phfinance",
]
KEYWORD = "Atome"
RATE_LIMIT_DELAY = 2.0  # 1 req / 2 sec


async def crawl_reddit(lookback_hours: int = 24):
    """Crawl Reddit for Atome mentions and run full pipeline."""
    logger.info(f"Starting Reddit crawl (lookback={lookback_hours}h)")
    all_posts = []

    async with httpx.AsyncClient(
        headers={"User-Agent": settings.reddit_user_agent},
        timeout=30.0,
    ) as client:
        for sub in SUBREDDITS:
            try:
                posts = await _search_subreddit(client, sub, lookback_hours)
                all_posts.extend(posts)
                logger.info(f"r/{sub}: found {len(posts)} posts")
            except Exception:
                logger.exception(f"Failed to crawl r/{sub}")
            await asyncio.sleep(RATE_LIMIT_DELAY)

    # Save to DB
    saved = await _save_posts(all_posts)
    logger.info(f"Reddit crawl complete: {len(all_posts)} found, {saved} new")

    # Run annotation pipeline
    await annotate_unannotated_posts()
    await cluster_posts()
    await check_and_send_alerts()


async def _search_subreddit(
    client: httpx.AsyncClient, subreddit: str, lookback_hours: int
) -> list[dict]:
    """Search a subreddit for Atome mentions."""
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": KEYWORD,
        "restrict_sr": "on",
        "sort": "new",
        "t": _reddit_time_filter(lookback_hours),
        "limit": 100,
    }

    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    posts = []

    for child in data.get("data", {}).get("children", []):
        item = child.get("data", {})
        created = datetime.utcfromtimestamp(item.get("created_utc", 0))
        if created < cutoff:
            continue

        text = f"{item.get('title', '')} {item.get('selftext', '')}".strip()

        # Filters
        if is_too_short(text):
            continue
        if not mentions_brand(text):
            continue
        author = item.get("author", "")
        if is_official_account(author):
            continue

        posts.append({
            "platform": "reddit",
            "brand": "atome_ph",
            "post_id": item.get("id", ""),
            "url": f"https://reddit.com{item.get('permalink', '')}",
            "author_handle": author,
            "content_text": text,
            "created_at": created,
            "engagement_likes": item.get("score", 0),
            "engagement_replies": item.get("num_comments", 0),
            "engagement_reposts": 0,
            "raw_json": item,
        })

    return posts


async def _save_posts(posts: list[dict]) -> int:
    """Save posts to DB with ON CONFLICT DO NOTHING."""
    async with async_session() as db:
        inserted = 0
        for p in posts:
            stmt = (
                insert(Post)
                .values(
                    platform=p["platform"],
                    brand=p["brand"],
                    post_id=p["post_id"],
                    url=p["url"],
                    author_handle=p["author_handle"],
                    content_text=p["content_text"],
                    created_at=p["created_at"],
                    engagement_likes=p["engagement_likes"],
                    engagement_replies=p["engagement_replies"],
                    engagement_reposts=p["engagement_reposts"],
                    raw_json=p.get("raw_json"),
                )
                .on_conflict_do_nothing(constraint="uq_platform_brand_post")
            )
            result = await db.execute(stmt)
            if result.rowcount > 0:
                inserted += 1
        await db.commit()
        return inserted


def _reddit_time_filter(lookback_hours: int) -> str:
    if lookback_hours <= 24:
        return "day"
    if lookback_hours <= 168:
        return "week"
    if lookback_hours <= 730:
        return "month"
    return "year"
