from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.incident import Incident
from backend.models.post import Post
from backend.schemas.analytics import (
    CategoryCount,
    CategoryResponse,
    ChannelResponse,
    ChannelStats,
    KPIOverview,
    SeverityCount,
    SeverityDistribution,
    TrendPoint,
    TrendResponse,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview", response_model=KPIOverview)
async def overview(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)

    total = (
        await db.execute(select(func.count()).select_from(Post).where(Post.created_at >= since))
    ).scalar() or 0

    negative = (
        await db.execute(
            select(func.count())
            .select_from(Post)
            .where(and_(Post.created_at >= since, Post.is_negative == True))
        )
    ).scalar() or 0

    critical_inc = (
        await db.execute(
            select(func.count())
            .select_from(Incident)
            .where(
                and_(
                    Incident.first_seen >= since,
                    Incident.severity.in_(["critical", "high"]),
                )
            )
        )
    ).scalar() or 0

    open_inc = (
        await db.execute(
            select(func.count())
            .select_from(Incident)
            .where(Incident.status.in_(["new", "acknowledged", "in_review"]))
        )
    ).scalar() or 0

    return KPIOverview(
        total_mentions=total,
        negative_complaints=negative,
        negative_pct=round(negative / total * 100, 1) if total else 0,
        critical_incidents=critical_inc,
        open_incidents=open_inc,
        avg_detect_to_alert_min=None,
    )


@router.get("/trend", response_model=TrendResponse)
async def trend(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    date_col = func.date(Post.created_at)

    rows = (
        await db.execute(
            select(
                date_col.label("date"),
                func.count().label("total"),
                func.count().filter(Post.severity == "critical").label("critical"),
                func.count().filter(Post.severity == "high").label("high"),
                func.count().filter(Post.severity == "medium").label("medium"),
                func.count().filter(Post.severity == "low").label("low"),
                func.count().filter(Post.severity == "none").label("none_sev"),
            )
            .where(Post.created_at >= since)
            .group_by(date_col)
            .order_by(date_col)
        )
    ).all()

    # Build lookup from DB rows
    data_by_date = {
        str(r.date): TrendPoint(
            date=str(r.date),
            total=r.total,
            critical=r.critical,
            high=r.high,
            medium=r.medium,
            low=r.low,
            none=r.none_sev,
        )
        for r in rows
    }

    # Fill all days in the range (including zeros)
    points = []
    today = datetime.utcnow().date()
    for i in range(days):
        d = today - timedelta(days=days - 1 - i)
        ds = str(d)
        if ds in data_by_date:
            points.append(data_by_date[ds])
        else:
            points.append(TrendPoint(date=ds, total=0, critical=0, high=0, medium=0, low=0, none=0))

    return TrendResponse(points=points)


@router.get("/categories", response_model=CategoryResponse)
async def categories(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        await db.execute(
            select(Post.category, func.count().label("cnt"))
            .where(and_(Post.created_at >= since, Post.category.isnot(None)))
            .group_by(Post.category)
            .order_by(func.count().desc())
        )
    ).all()

    total = sum(r.cnt for r in rows) or 1
    return CategoryResponse(
        items=[
            CategoryCount(category=r.category, count=r.cnt, pct=round(r.cnt / total * 100, 1))
            for r in rows
        ]
    )


@router.get("/channels", response_model=ChannelResponse)
async def channels(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        await db.execute(
            select(
                Post.platform,
                func.count().label("total"),
                func.count().filter(Post.is_negative == True).label("negative"),
            )
            .where(Post.created_at >= since)
            .group_by(Post.platform)
        )
    ).all()

    return ChannelResponse(
        items=[
            ChannelStats(platform=r.platform, total=r.total, negative=r.negative) for r in rows
        ]
    )


@router.get("/severity-distribution", response_model=SeverityDistribution)
async def severity_distribution(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        await db.execute(
            select(Post.severity, func.count().label("cnt"))
            .where(and_(Post.created_at >= since, Post.severity.isnot(None)))
            .group_by(Post.severity)
        )
    ).all()

    total = sum(r.cnt for r in rows) or 1
    return SeverityDistribution(
        items=[
            SeverityCount(severity=r.severity, count=r.cnt, pct=round(r.cnt / total * 100, 1))
            for r in rows
        ],
        total=total,
    )
