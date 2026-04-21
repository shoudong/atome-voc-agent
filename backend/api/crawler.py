"""POST /crawler/run — trigger a crawl job."""

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db

router = APIRouter(prefix="/api/crawler", tags=["crawler"])


class CrawlRequest(BaseModel):
    platform: str  # twitter | reddit | all
    lookback_hours: int = 24


class CrawlResponse(BaseModel):
    status: str
    message: str


@router.post("/run", response_model=CrawlResponse)
async def trigger_crawl(
    req: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a crawl job for the specified platform."""
    from backend.services.crawler_reddit import crawl_reddit
    from backend.services.crawler_twitter import crawl_twitter

    if req.platform in ("reddit", "all"):
        background_tasks.add_task(crawl_reddit, req.lookback_hours)
    if req.platform in ("twitter", "all"):
        background_tasks.add_task(crawl_twitter, req.lookback_hours)

    return CrawlResponse(
        status="started",
        message=f"Crawl job started for {req.platform} (lookback={req.lookback_hours}h)",
    )
