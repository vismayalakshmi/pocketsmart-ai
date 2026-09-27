import json
from typing import Any

from google import genai
from google.genai import types

from config import settings


_client = None


if settings.gemini_api_key:
    try:
        _client = genai.Client(
            api_key=settings.gemini_api_key
        )
    except Exception:
        _client = None


def _json_from_text(text: str) -> dict:
    """
    Convert Gemini's response into a Python dictionary.
    """

    text = (text or "").strip()

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    if text.startswith("```"):
        text = text.replace(
            "```json",
            "",
            1,
        )

        text = text.replace(
            "```",
            "",
            1,
        ).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        text = text[start:end + 1]

    return json.loads(text)


def generate_json(
    prompt: str,
    contents=None,
) -> dict:
    """
    Send a request to Gemini and expect JSON.
    """

    if settings.demo_mode:
        raise RuntimeError("DEMO_FALLBACK")

    if _client is None:
        raise RuntimeError(
            "Gemini client is not configured."
        )

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=contents if contents is not None else prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    return _json_from_text(
        response.text
    )


def home_plan(data):
    """
    Deterministic fallback planner.
    """

    budget = float(data.budget)

    lights_count = max(
        int(data.lights),
        1,
    )

    fans_count = max(
        int(data.fans),
        1,
    )

    furniture_count = max(
        int(data.furniture),
        1,
    )

    lighting_budget = budget * 0.20
    fan_budget = budget * 0.17
    furniture_budget = budget * 0.55

    used_budget = (
        lighting_budget
        + fan_budget
        + furniture_budget
    )

    remaining_budget = budget - used_budget

    rooms = (
        ", ".join(data.rooms)
        if data.rooms
        else "the most frequently used rooms"
    )

    return {
        "total_budget": round(
            budget,
            2,
        ),

        "remaining_budget": round(
            remaining_budget,
            2,
        ),

        "categories": [
            {
                "category": "Lighting",

                "allocation": round(
                    lighting_budget,
                    2,
                ),

                "items": [
                    {
                        "item": "LED ceiling lights",

                        "description":
                            "Energy-efficient "
                            "ceiling lighting.",

                        "price": round(
                            lighting_budget
                            / lights_count,
                            2,
                        ),

                        "quantity": lights_count,

                        "shopping_url":
                            "https://www.amazon.in/"
                            "s?k=LED+ceiling+light",
                    }
                ],
            },

            {
                "category": "Fans",

                "allocation": round(
                    fan_budget,
                    2,
                ),

                "items": [
                    {
                        "item": "Ceiling fan",

                        "description":
                            "Energy-efficient "
                            "ceiling fan.",

                        "price": round(
                            fan_budget
                            / fans_count,
                            2,
                        ),

                        "quantity": fans_count,

                        "shopping_url":
                            "https://www.amazon.in/"
                            "s?k=ceiling+fan",
                    }
                ],
            },

            {
                "category": "Furniture",

                "allocation": round(
                    furniture_budget,
                    2,
                ),

                "items": [
                    {
                        "item":
                            "Essential furniture package",

                        "description":
                            "Prioritize essential "
                            "pieces for selected rooms.",

                        "price": round(
                            furniture_budget
                            / furniture_count,
                            2,
                        ),

                        "quantity": furniture_count,

                        "shopping_url":
                            "https://www.ikea.com/in/en/"
                            "search/?q=furniture",
                    }
                ],
            },
        ],

        "suggestions": [
            "Keep some money as contingency "
            "for delivery and installation.",

            "Buy essential furniture first "
            "before decorative items.",

            f"Prioritize rooms: {rooms}.",

            (
                f"Preferences considered: "
                f"{data.preferences or 'None'}."
            ),
        ],

        "source": "demo",
    }


def party_plan(data):
    """
    Deterministic fallback party planner.
    """

    budget = float(data.budget)

    food = budget * 0.45
    venue = budget * 0.20
    decoration = budget * 0.12
    entertainment = budget * 0.08

    used = (
        food
        + venue
        + decoration
        + entertainment
    )

    contingency = budget - used

    food_per_guest = (
        food / data.guests
    )

    return {
        "total_budget": round(
            budget,
            2,
        ),

        "remaining_budget": round(
            contingency,
            2,
        ),

        "categories": [
            {
                "category": "Food",

                "allocation": round(
                    food,
                    2,
                ),

                "items": [
                    {
                        "item":
                            data.food_preference
                            or "Mixed menu",

                        "description":
                            f"Food planning for "
                            f"{data.guests} guests.",

                        "price": round(
                            food,
                            2,
                        ),

                        "quantity": 1,

                        "shopping_url":
                            "https://www.swiggy.com/",
                    }
                ],
            },

            {
                "category": "Venue",

                "allocation": round(
                    venue,
                    2,
                ),

                "items": [
                    {
                        "item":
                            data.venue_preference
                            or "Event venue",

                        "description":
                            data.event_type,

                        "price": round(
                            venue,
                            2,
                        ),

                        "quantity": 1,

                        "shopping_url":
                            "https://www.google.com/"
                            "search?q=party+venues",
                    }
                ],
            },

            {
                "category": "Decoration",

                "allocation": round(
                    decoration,
                    2,
                ),

                "items": [
                    {
                        "item":
                            "Theme decoration",

                        "description":
                            "Balloons, backdrop "
                            "and table decoration.",

                        "price": round(
                            decoration,
                            2,
                        ),

                        "quantity": 1,

                        "shopping_url":
                            "https://www.amazon.in/"
                            "s?k=party+decorations",
                    }
                ],
            },

            {
                "category": "Entertainment",

                "allocation": round(
                    entertainment,
                    2,
                ),

                "items": [
                    {
                        "item":
                            "Music and activities",

                        "description":
                            "Simple activities "
                            "within the event budget.",

                        "price": round(
                            entertainment,
                            2,
                        ),

                        "quantity": 1,

                        "shopping_url":
                            "https://www.google.com/"
                            "search?q=party+entertainment",
                    }
                ],
            },
        ],

        "suggestions": [
            (
                "Approximate food budget per "
                f"guest: ₹{food_per_guest:,.0f}."
            ),

            "Confirm venue, catering and "
            "cancellation terms before paying.",

            "Keep the remaining amount as "
            "contingency instead of spending "
            "the entire budget.",
        ],

        "source": "demo",
    }


def jewelry_plan(
    image_bytes: bytes,
    mime_type: str,
    budget: float,
    preferences: str,
):
    """
    Multimodal jewelry planner.
    """

    if settings.demo_mode or _client is None:

        return {
            "outfit_analysis": {
                "colors": "Demo image analysis",
                "style": "Versatile",
                "formality": "Semi-formal",
            },

            "recommendations": [
                {
                    "item":
                        "Minimal pendant set",

                    "description":
                        "A versatile option "
                        "that does not overpower "
                        "the outfit.",

                    "price": 900,

                    "quantity": 1,

                    "shopping_url":
                        "https://www.myntra.com/"
                        "jewellery",
                },

                {
                    "item":
                        "Stud earrings",

                    "description":
                        "Simple matching studs.",

                    "price": 600,

                    "quantity": 1,

                    "shopping_url":
                        "https://www.ajio.com/"
                        "search/?text=earrings",
                },

                {
                    "item":
                        "Bangle set",

                    "description":
                        "Use only if it "
                        "complements the outfit.",

                    "price": 750,

                    "quantity": 1,

                    "shopping_url":
                        "https://www.myntra.com/"
                        "bangles",
                },
            ],

            "styling_tips": [
                "Match the metal tone with "
                "the outfit's overall palette.",

                "For heavily detailed outfits, "
                "keep jewelry simpler.",

                "Check the total price before "
                "purchasing.",
            ],

            "estimated_total": 2250,

            "source": "demo",
        }

    prompt = f"""
Analyze the uploaded outfit image and provide
a jewelry styling recommendation.

Budget: ₹{budget:.2f}

Preferences:
{preferences or "None"}

Return JSON with:

outfit_analysis:
- colors
- style
- formality

recommendations:
- item
- description
- price
- quantity
- shopping_url

styling_tips:
array of strings

estimated_total:
number

Do not claim exact product availability.
Use broad shopping/search URLs.
"""

    response = _client.models.generate_content(
        model=settings.gemini_model,

        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),

            prompt,
        ],

        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    result = _json_from_text(
        response.text
    )

    result["source"] = "gemini"

    return result