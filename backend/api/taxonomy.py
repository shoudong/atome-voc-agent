from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.taxonomy import TaxonomyCategory, TaxonomySubIssue

router = APIRouter(prefix="/api/taxonomy", tags=["taxonomy"])


# --- Category schemas ---
class CategoryCreate(BaseModel):
    key: str
    label: str
    description: str | None = None
    color: str | None = None
    sort_order: int = 0


class CategoryOut(BaseModel):
    id: int
    key: str
    label: str
    description: str | None
    color: str | None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class CategoryUpdate(BaseModel):
    label: str | None = None
    description: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


# --- Sub-issue schemas ---
class SubIssueCreate(BaseModel):
    key: str
    label: str
    category_key: str | None = None
    description: str | None = None


class SubIssueOut(BaseModel):
    id: int
    key: str
    label: str
    category_key: str | None
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


# --- Category endpoints ---
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(TaxonomyCategory).order_by(TaxonomyCategory.sort_order)
        )
    ).scalars().all()
    return [CategoryOut.model_validate(r) for r in rows]


@router.post("/categories", response_model=CategoryOut)
async def create_category(cat: CategoryCreate, db: AsyncSession = Depends(get_db)):
    record = TaxonomyCategory(**cat.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return CategoryOut.model_validate(record)


@router.patch("/categories/{cat_id}", response_model=CategoryOut)
async def update_category(
    cat_id: int, update: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    cat = (
        await db.execute(select(TaxonomyCategory).where(TaxonomyCategory.id == cat_id))
    ).scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    await db.commit()
    await db.refresh(cat)
    return CategoryOut.model_validate(cat)


# --- Sub-issue endpoints ---
@router.get("/sub-issues", response_model=list[SubIssueOut])
async def list_sub_issues(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(TaxonomySubIssue))).scalars().all()
    return [SubIssueOut.model_validate(r) for r in rows]


@router.post("/sub-issues", response_model=SubIssueOut)
async def create_sub_issue(si: SubIssueCreate, db: AsyncSession = Depends(get_db)):
    record = TaxonomySubIssue(**si.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return SubIssueOut.model_validate(record)
