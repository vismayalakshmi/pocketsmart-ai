import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.ai import (
    generate_json,
    home_plan,
    jewelry_plan,
    party_plan,
)
from app.auth import (
    current_user,
    hash_password,
    verify_password,
)
from app.config import settings
from app.db import (
    add_history,
    create_user,
    get_history_item,
    get_user_by_username,
    init_db,
    list_history,
)
from app.schemas import (
    HomeRequest,
    PartyRequest,
)


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="PocketSmart AI",
    description=(
        "Generative AI budget and "
        "recommendation platform."
    ),
    version="2.0.0",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=False,
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.on_event("startup")
def startup():
    init_db()


def require_user(request: Request):
    user = current_user(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login required.",
        )

    return user


def save_plan(
    user,
    plan_type,
    budget,
    payload,
    result,
):
    add_history(
        history_id=str(uuid.uuid4()),
        user_id=user["id"],
        plan_type=plan_type,
        budget=budget,
        created_at=datetime.now(
            timezone.utc
        ).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        input_json=json.dumps(
            payload,
            ensure_ascii=False,
        ),
        result_json=json.dumps(
            result,
            ensure_ascii=False,
        ),
    )


# -------------------------
# GENERAL
# -------------------------


@app.get(
    "/api/health"
)
def health():
    return {
        "status": "ok",
        "app": "PocketSmart AI",
        "ai_configured":
            bool(settings.gemini_api_key),
        "demo_mode":
            settings.demo_mode,
        "model":
            settings.gemini_model,
    }


@app.get(
    "/",
    response_class=HTMLResponse,
)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": current_user(request),
        },
    )


# -------------------------
# AUTHENTICATION
# -------------------------


@app.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
        },
    )


@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return JSONResponse(
            {
                "error":
                    "Username must contain "
                    "at least 3 characters."
            },
            status_code=400,
        )

    if len(password) < 6:
        return JSONResponse(
            {
                "error":
                    "Password must contain "
                    "at least 6 characters."
            },
            status_code=400,
        )

    if get_user_by_username(username):
        return JSONResponse(
            {
                "error":
                    "Username already exists."
            },
            status_code=400,
        )

    try:
        create_user(
            username=username,
            email=email,
            password_hash=hash_password(
                password
            ),
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    except Exception:
        return JSONResponse(
            {
                "error":
                    "Username or email "
                    "already exists."
            },
            status_code=400,
        )

    return RedirectResponse(
        "/login?registered=1",
        status_code=303,
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "registered":
                request.query_params.get(
                    "registered"
                ),
        },
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_username(
        username.strip()
    )

    if not user:
        return JSONResponse(
            {
                "error":
                    "Invalid username "
                    "or password."
            },
            status_code=401,
        )

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return JSONResponse(
            {
                "error":
                    "Invalid username "
                    "or password."
            },
            status_code=401,
        )

    request.session["user_id"] = user["id"]

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        "/login",
        status_code=303,
    )


# -------------------------
# DASHBOARD
# -------------------------


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
        },
    )


@app.get(
    "/home-planner",
    response_class=HTMLResponse,
)
def home_page(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    return templates.TemplateResponse(
        "home_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


@app.get(
    "/party-planner",
    response_class=HTMLResponse,
)
def party_page(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    return templates.TemplateResponse(
        "party_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


@app.get(
    "/jewelry-planner",
    response_class=HTMLResponse,
)
def jewelry_page(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    return templates.TemplateResponse(
        "jewelry_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


# -------------------------
# HISTORY
# -------------------------


@app.get(
    "/history",
    response_class=HTMLResponse,
)
def history_page(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    rows = list_history(
        user["id"]
    )

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "user": user,
            "history": rows,
        },
    )


@app.get(
    "/recommendations-details/{history_id}",
    response_class=HTMLResponse,
)
def history_details(
    request: Request,
    history_id: str,
):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login"
        )

    row = get_history_item(
        user["id"],
        history_id,
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="History item not found.",
        )

    return templates.TemplateResponse(
        "history_detail.html",
        {
            "request": request,
            "user": user,
            "item": row,
            "result": json.loads(
                row["result_json"]
            ),
        },
    )


# -------------------------
# API SESSION
# -------------------------


@app.get(
    "/api/session-info"
)
def session_info(request: Request):
    user = current_user(request)

    return {
        "authenticated": bool(user),
        "username":
            user["username"]
            if user
            else None,
    }


@app.get(
    "/api/recommendation-history"
)
def recommendation_history(
    request: Request,
):
    user = require_user(request)

    return [
        dict(row)
        for row in list_history(
            user["id"]
        )
    ]


# -------------------------
# HOME INTERIOR AI
# -------------------------


@app.post(
    "/api/home-planner"
)
def home_planner(
    request: Request,
    data: HomeRequest,
):
    user = require_user(request)

    prompt = f"""
Create a practical home interior
budget plan in Indian Rupees.

Budget:
₹{data.budget}

Lights:
{data.lights}

Fans:
{data.fans}

Furniture pieces:
{data.furniture}

Rooms:
{", ".join(data.rooms)}

Preferences:
{data.preferences or "None"}

Return JSON containing:

total_budget
remaining_budget
categories
suggestions

Each category must contain:

category
allocation
items

Each item must contain:

item
description
price
quantity
shopping_url

Keep all allocations within
the supplied budget.
"""

    try:
        result = generate_json(
            prompt
        )

        result["source"] = "gemini"

    except Exception:
        result = home_plan(
            data
        )

    save_plan(
        user=user,
        plan_type="Home Interior Budget",
        budget=data.budget,
        payload=data.model_dump(),
        result=result,
    )

    return result


# -------------------------
# PARTY AI
# -------------------------


@app.post(
    "/api/party-planner"
)
def party_planner(
    request: Request,
    data: PartyRequest,
):
    user = require_user(request)

    prompt = f"""
Create a practical party budget
plan in Indian Rupees.

Budget:
₹{data.budget}

Guests:
{data.guests}

Event type:
{data.event_type}

Food preference:
{data.food_preference}

Venue preference:
{data.venue_preference}

Other preferences:
{data.preferences}

Return JSON containing:

total_budget
remaining_budget
categories
suggestions

Each category must contain:

category
allocation
items

Each item must contain:

item
description
price
quantity
shopping_url

Keep all allocations within
the supplied budget.
"""

    try:
        result = generate_json(
            prompt
        )

        result["source"] = "gemini"

    except Exception:
        result = party_plan(
            data
        )

    save_plan(
        user=user,
        plan_type="Party Budget",
        budget=data.budget,
        payload=data.model_dump(),
        result=result,
    )

    return result


# -------------------------
# JEWELRY AI
# -------------------------


@app.post(
    "/api/jewelry-planner"
)
async def jewelry_planner(
    request: Request,
    budget: float = Form(...),
    preferences: str = Form(""),
    image: UploadFile = File(...),
):
    user = require_user(request)

    if budget <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Budget must be "
                "greater than zero."
            ),
        )

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Upload a JPG, PNG "
                "or WEBP image."
            ),
        )

    image_bytes = await image.read()

    max_size = 8 * 1024 * 1024

    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail=(
                "Image must be "
                "8 MB or smaller."
            ),
        )

    try:
        result = jewelry_plan(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            budget=budget,
            preferences=preferences,
        )

    except Exception:
        result = jewelry_plan(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            budget=budget,
            preferences=preferences,
        )

    save_plan(
        user=user,
        plan_type="Jewelry Styling",
        budget=budget,
        payload={
            "budget": budget,
            "preferences": preferences,
            "filename": image.filename,
        },
        result=result,
    )

    return result