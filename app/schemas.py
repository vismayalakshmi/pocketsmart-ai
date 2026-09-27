from typing import List

from pydantic import BaseModel, Field


class HomeRequest(BaseModel):
    budget: float = Field(gt=0)

    lights: int = Field(
        default=0,
        ge=0,
    )

    fans: int = Field(
        default=0,
        ge=0,
    )

    furniture: int = Field(
        default=0,
        ge=0,
    )

    rooms: List[str] = Field(
        default_factory=list
    )

    preferences: str = ""


class PartyRequest(BaseModel):
    budget: float = Field(gt=0)

    guests: int = Field(gt=0)

    event_type: str = "Birthday"

    food_preference: str = ""

    venue_preference: str = ""

    preferences: str = ""


class Item(BaseModel):
    item: str

    description: str = ""

    price: float = 0

    quantity: int = 1

    shopping_url: str = ""


class Category(BaseModel):
    category: str

    allocation: float = 0

    items: List[Item] = Field(
        default_factory=list
    )


class PlannerResult(BaseModel):
    total_budget: float

    remaining_budget: float

    categories: List[Category] = Field(
        default_factory=list
    )

    suggestions: List[str] = Field(
        default_factory=list
    )

    source: str = "gemini"


class JewelryResult(BaseModel):
    outfit_analysis: dict = Field(
        default_factory=dict
    )

    recommendations: List[Item] = Field(
        default_factory=list
    )

    styling_tips: List[str] = Field(
        default_factory=list
    )

    estimated_total: float = 0

    source: str = "gemini"