"""
login.py - Login & Registration System
"""

import csv
import hashlib
import os
from utils import (
    log_action, validate_input, catch_errors,
    validate_username, validate_password,
    USERS_CSV, ensure_data_dir, logger
)


def _hash_password(password: str) -> str:
    """SHA-256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    """Load users from CSV into {username: hashed_password} dict."""
    ensure_data_dir()
    users = {}
    if not os.path.exists(USERS_CSV):
        return users
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row["username"]] = row["password"]
    return users


def _save_user(username: str, hashed_password: str):
    """Append a new user to the CSV."""
    ensure_data_dir()
    file_exists = os.path.exists(USERS_CSV)
    with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"username": username, "password": hashed_password})


@log_action("User Login")
@catch_errors
def authenticate(username: str, password: str) -> bool:
    """Return True if credentials are valid."""
    validate_username(username)
    validate_password(password)
    users = _load_users()
    hashed = _hash_password(password)
    if username in users and users[username] == hashed:
        logger.info(f"Login SUCCESS for user: {username}")
        return True
    logger.warning(f"Login FAILED for user: {username}")
    return False


@log_action("User Registration")
@catch_errors
def register(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    try:
        validate_username(username)
        validate_password(password)
    except ValueError as e:
        return False, str(e)

    users = _load_users()
    if username in users:
        return False, "Username already exists. Please choose another."

    _save_user(username, _hash_password(password))
    logger.info(f"Registered new user: {username}")
    return True, "Registration successful! You can now log in."
