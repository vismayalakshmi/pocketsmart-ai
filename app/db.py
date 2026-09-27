import sqlite3
from contextlib import contextmanager

from app.config import settings


def connect():
    connection = sqlite3.connect(settings.database_path)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


@contextmanager
def db():
    connection = connect()

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def init_db():
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                budget REAL,
                created_at TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,

                FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
            );
            """
        )


def get_user_by_username(username: str):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()


def get_user_by_email(email: str):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()


def get_user_by_id(user_id: int):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()


def create_user(
    username: str,
    email: str,
    password_hash: str,
    created_at: str,
):
    with db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                created_at,
            ),
        )

        return cursor.lastrowid


def add_history(
    history_id,
    user_id,
    plan_type,
    budget,
    created_at,
    input_json,
    result_json,
):
    with db() as connection:
        connection.execute(
            """
            INSERT INTO history
            (
                id,
                user_id,
                plan_type,
                budget,
                created_at,
                input_json,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                history_id,
                user_id,
                plan_type,
                budget,
                created_at,
                input_json,
                result_json,
            ),
        )


def list_history(user_id: int):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()


def get_history_item(
    user_id: int,
    history_id: str,
):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM history
            WHERE id = ?
            AND user_id = ?
            """,
            (
                history_id,
                user_id,
            ),
        ).fetchone()