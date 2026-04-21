"""Rule-based severity calculator with overrides on top of LLM severity."""

SEVERITY_ORDER = ["none", "low", "medium", "high", "critical"]

# Categories that warrant minimum severity floors
HIGH_RISK_CATEGORIES = {"debt_collection", "fraud", "security"}
MEDIUM_RISK_CATEGORIES = {"interest_rate", "refund"}

# Engagement thresholds
ENGAGEMENT_CRITICAL_THRESHOLD = 1000  # auto-critical if any engagement metric exceeds
ENGAGEMENT_HIGH_THRESHOLD = 500


def severity_index(sev: str) -> int:
    try:
        return SEVERITY_ORDER.index(sev)
    except ValueError:
        return 0


def apply_severity_overrides(
    llm_severity: str,
    category: str | None,
    engagement_likes: int = 0,
    engagement_replies: int = 0,
    engagement_reposts: int = 0,
    cluster_post_count: int | None = None,
) -> str:
    """
    Apply rule-based overrides to the LLM-assigned severity.

    Rules:
    1. High engagement (>1K any metric) -> auto-critical
    2. High-risk categories (debt_collection, fraud, security) -> min medium
    3. Medium-risk categories (interest_rate, refund) -> min low
    4. Cluster recurrence (>10 posts in 48h) -> min high
    5. High engagement (>500) -> min high
    """
    current = severity_index(llm_severity)
    max_engagement = max(engagement_likes, engagement_replies, engagement_reposts)

    # Rule 1: Viral content -> critical
    if max_engagement >= ENGAGEMENT_CRITICAL_THRESHOLD:
        return "critical"

    # Rule 2: High-risk category floor
    if category in HIGH_RISK_CATEGORIES:
        current = max(current, severity_index("medium"))

    # Rule 3: Medium-risk category floor
    if category in MEDIUM_RISK_CATEGORIES:
        current = max(current, severity_index("low"))

    # Rule 4: Cluster recurrence
    if cluster_post_count is not None and cluster_post_count > 10:
        current = max(current, severity_index("high"))

    # Rule 5: High engagement floor
    if max_engagement >= ENGAGEMENT_HIGH_THRESHOLD:
        current = max(current, severity_index("high"))

    return SEVERITY_ORDER[current]
