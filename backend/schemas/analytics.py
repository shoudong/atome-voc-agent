from pydantic import BaseModel


class KPIOverview(BaseModel):
    total_mentions: int
    negative_complaints: int
    negative_pct: float
    critical_incidents: int
    open_incidents: int
    avg_detect_to_alert_min: float | None


class TrendPoint(BaseModel):
    date: str
    total: int
    critical: int
    high: int
    medium: int
    low: int
    none: int


class TrendResponse(BaseModel):
    points: list[TrendPoint]


class CategoryCount(BaseModel):
    category: str
    count: int
    pct: float


class CategoryResponse(BaseModel):
    items: list[CategoryCount]


class ChannelStats(BaseModel):
    platform: str
    total: int
    negative: int
    top_subreddits: list[dict] | None = None
    top_keywords: list[dict] | None = None


class ChannelResponse(BaseModel):
    items: list[ChannelStats]


class SeverityCount(BaseModel):
    severity: str
    count: int
    pct: float


class SeverityDistribution(BaseModel):
    items: list[SeverityCount]
    total: int
