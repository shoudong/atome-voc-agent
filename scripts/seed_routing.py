"""Seed the routing_rules table with default category-to-department routing."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from backend.database import async_session
from backend.models.routing import RoutingRule

RULES = [
    {
        "category": "debt_collection",
        "severity_min": "low",
        "departments": ["Collections", "Compliance"],
        "escalate_to": ["CEO Office"],
        "channels": ["slack", "lark"],
    },
    {
        "category": "transaction",
        "severity_min": "low",
        "departments": ["Product", "CS", "Ops"],
        "escalate_to": None,
        "channels": ["slack"],
    },
    {
        "category": "app_bug",
        "severity_min": "low",
        "departments": ["Product", "Engineering"],
        "escalate_to": None,
        "channels": ["slack"],
    },
    {
        "category": "interest_rate",
        "severity_min": "low",
        "departments": ["CEO Office", "Compliance", "PR"],
        "escalate_to": ["CEO Office"],
        "channels": ["slack", "email"],
    },
    {
        "category": "fraud",
        "severity_min": "medium",
        "departments": ["Risk", "Security"],
        "escalate_to": ["CEO Office"],
        "channels": ["slack", "lark", "email"],
    },
    {
        "category": "security",
        "severity_min": "medium",
        "departments": ["Risk", "Security"],
        "escalate_to": ["CEO Office"],
        "channels": ["slack", "lark", "email"],
    },
    {
        "category": "customer_service",
        "severity_min": "low",
        "departments": ["CS Head", "CS Ops"],
        "escalate_to": None,
        "channels": ["slack"],
    },
    {
        "category": "refund",
        "severity_min": "low",
        "departments": ["Product", "CS"],
        "escalate_to": None,
        "channels": ["slack"],
    },
    {
        "category": "spend_limit",
        "severity_min": "low",
        "departments": ["Product", "Risk"],
        "escalate_to": None,
        "channels": ["slack"],
    },
    {
        "category": "account",
        "severity_min": "low",
        "departments": ["Product", "CS"],
        "escalate_to": None,
        "channels": ["slack"],
    },
]


async def seed():
    async with async_session() as db:
        for rule in RULES:
            existing = (
                await db.execute(
                    select(RoutingRule).where(RoutingRule.category == rule["category"])
                )
            ).scalar_one_or_none()
            if not existing:
                db.add(RoutingRule(**rule))
                print(f"  + Routing rule: {rule['category']} -> {rule['departments']}")

        await db.commit()
        print("Routing rules seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
