"""X/Twitter crawler using Brave Search API."""

import logging
import re
from datetime import datetime, timedelta

import httpx

from backend.database import async_session
from backend.models.post import Post
from backend.services.dedup import is_official_account, is_noise_account, is_ph_relevant, is_too_short, mentions_brand
from backend.services.llm_annotator import annotate_unannotated_posts
from backend.services.clustering import cluster_posts
from backend.services.alerting import check_and_send_alerts
from backend.config import settings

from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

KEYWORDS = [
    "Atome credit card Philippines",
    "Atome scam Philippines",
    "Atome refund Philippines",
    "Atome BNPL complaint",
    "Atome payment failed",
    "Atome credit limit",
    "Atome collection Philippines",
    "Atome overdue Philippines",
    "Atome debt collection",
    "Atome home visit",
    "Atome harassment",
    "Atome threatening",
    # Taglish / Filipino keywords
    "Atome bayad",
    "Atome hindi mabayaran",
    "Atome nabawasan limit",
    "Atome OTP di gumagana",
    "Atome ang laki ng interest",
    "Atome nagbabanta",
    "Atome tumawag collection",
]


async def crawl_twitter(lookback_hours: int = 24):
    """Crawl X/Twitter via Brave Search for Atome mentions."""
    if not settings.brave_api_key:
        logger.warning("BRAVE_API_KEY not set, skipping Twitter crawl")
        return

    logger.info(f"Starting Twitter/X crawl via Brave Search (lookback={lookback_hours}h)")
    all_posts = []
    seen_urls = set()

    async with httpx.AsyncClient(timeout=30.0) as client:
        for keyword in KEYWORDS:
            try:
                posts = await _brave_search(client, keyword, lookback_hours)
                for p in posts:
                    if p["url"] not in seen_urls:
                        seen_urls.add(p["url"])
                        all_posts.append(p)
                logger.info(f"Keyword '{keyword}': found {len(posts)} results")
            except Exception:
                logger.exception(f"Failed to search keyword '{keyword}'")

    saved = await _save_posts(all_posts)
    logger.info(f"Twitter/X crawl complete: {len(all_posts)} found, {saved} new")

    await annotate_unannotated_posts()
    await cluster_posts()
    await check_and_send_alerts()


async def _brave_search(
    client: httpx.AsyncClient, keyword: str, lookback_hours: int
) -> list[dict]:
    """Search Brave for X/Twitter posts matching keyword."""
    query = f"site:x.com {keyword}"

    params: dict = {"q": query, "count": 20}
    # Only add freshness filter for short lookbacks — longer ones need all results
    if lookback_hours <= 24:
        params["freshness"] = "pd"
    elif lookback_hours <= 168:
        params["freshness"] = "pw"
    elif lookback_hours <= 730:
        params["freshness"] = "pm"
    # For 90d+, skip freshness filter to get max results

    resp = await client.get(
        BRAVE_SEARCH_URL,
        params=params,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.brave_api_key,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    posts = []
    for result in data.get("web", {}).get("results", []):
        url = result.get("url", "")

        # Only keep x.com or twitter.com status URLs
        if not _is_tweet_url(url):
            continue

        title = result.get("title", "")
        description = result.get("description", "")
        text = f"{title} {description}".strip()

        # Extract author handle from URL
        author = _extract_handle(url)

        # Parse post ID from URL
        post_id = _extract_post_id(url)
        if not post_id:
            continue

        # Parse date if available
        age = result.get("age", "")
        page_age = result.get("page_age", "")
        created = _parse_brave_date(page_age or age)

        # Filters
        if is_too_short(text):
            continue
        if not mentions_brand(text):
            continue
        if is_official_account(author):
            continue
        if is_noise_account(author):
            continue
        if not is_ph_relevant(text):
            continue

        posts.append({
            "platform": "twitter",
            "brand": "atome_ph",
            "post_id": post_id,
            "url": url,
            "author_handle": author,
            "content_text": text,
            "created_at": created,
            "engagement_likes": 0,
            "engagement_replies": 0,
            "engagement_reposts": 0,
            "raw_json": result,
        })

    return posts


def _is_tweet_url(url: str) -> bool:
    """Check if URL is an individual tweet/post."""
    return bool(re.search(r"(x\.com|twitter\.com)/\w+/status/\d+", url))


def _extract_handle(url: str) -> str:
    """Extract @handle from tweet URL."""
    match = re.search(r"(?:x\.com|twitter\.com)/(\w+)/status/", url)
    return match.group(1) if match else ""


def _extract_post_id(url: str) -> str:
    """Extract tweet ID from URL."""
    match = re.search(r"/status/(\d+)", url)
    return match.group(1) if match else ""


def _parse_brave_date(date_str: str) -> datetime:
    """Parse Brave's date/age string into a datetime."""
    if not date_str:
        return datetime.utcnow()

    # Brave returns ISO dates like "2026-04-20T..."
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, TypeError):
        pass

    # Or relative ages like "1 day ago", "3 hours ago"
    now = datetime.utcnow()
    match = re.search(r"(\d+)\s*(hour|day|week|month)", date_str.lower())
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == "hour":
            return now - timedelta(hours=num)
        elif unit == "day":
            return now - timedelta(days=num)
        elif unit == "week":
            return now - timedelta(weeks=num)
        elif unit == "month":
            return now - timedelta(days=num * 30)

    return now


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
