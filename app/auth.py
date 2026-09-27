from fastapi import Request
from pwdlib import PasswordHash

from app.db import get_user_by_id


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_hash.verify(
            password,
            hashed_password,
        )
    except Exception:
        return False


def current_user(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    try:
        return get_user_by_id(int(user_id))
    except (TypeError, ValueError):
        return None