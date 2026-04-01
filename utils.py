"""
utils.py - Utility functions, decorators, and constants for Student Toolkit
"""

import functools
import logging
import datetime
import os
import re

# ─────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────
LOG_FILE = "activity.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("StudentToolkit")


# ─────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────

def log_action(action_name: str):
    """Decorator factory: logs when a function is called."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"ACTION: {action_name} | Function: {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"DONE:   {action_name} | Function: {func.__name__}")
            return result
        return wrapper
    return decorator


def validate_input(func):
    """Decorator: strips string inputs and re-raises ValueError with context."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cleaned_args = []
        for a in args:
            cleaned_args.append(a.strip() if isinstance(a, str) else a)
        cleaned_kwargs = {k: (v.strip() if isinstance(v, str) else v) for k, v in kwargs.items()}
        try:
            return func(*cleaned_args, **cleaned_kwargs)
        except ValueError as e:
            logger.warning(f"Validation failed in {func.__name__}: {e}")
            raise
    return wrapper


def catch_errors(func):
    """Decorator: catches unexpected exceptions and logs them."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"ERROR in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


# ─────────────────────────────────────────────
# Validation Helpers
# ─────────────────────────────────────────────

@validate_input
def validate_username(username: str) -> str:
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters.")
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValueError("Username can only contain letters, numbers, and underscores.")
    return username


@validate_input
def validate_password(password: str) -> str:
    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters.")
    return password


@validate_input
def validate_positive_float(value: str, field: str = "Value") -> float:
    try:
        v = float(value)
    except ValueError:
        raise ValueError(f"{field} must be a number.")
    if v <= 0:
        raise ValueError(f"{field} must be greater than 0.")
    return v


@validate_input
def validate_positive_int(value: str, field: str = "Value") -> int:
    try:
        v = int(value)
    except ValueError:
        raise ValueError(f"{field} must be a whole number.")
    if v <= 0:
        raise ValueError(f"{field} must be greater than 0.")
    return v


# ─────────────────────────────────────────────
# Constants / Theme Colors
# ─────────────────────────────────────────────

THEME = {
    "bg_dark":       "#0D0D1A",
    "bg_card":       "#12122A",
    "bg_sidebar":    "#0A0A1F",
    "accent":        "#6C63FF",
    "accent2":       "#00D4FF",
    "accent3":       "#FF6B6B",
    "accent4":       "#4ECDC4",
    "accent5":       "#FFE66D",
    "text_primary":  "#FFFFFF",
    "text_secondary":"#A0A0C0",
    "success":       "#2ECC71",
    "warning":       "#F39C12",
    "error":         "#E74C3C",
    "border":        "#2A2A4A",
    "hover":         "#1E1E3E",
    "gradient_from": "#6C63FF",
    "gradient_to":   "#00D4FF",
}

FONT_FAMILY = "Segoe UI"

FONTS = {
    "title":    (FONT_FAMILY, 26, "bold"),
    "heading":  (FONT_FAMILY, 18, "bold"),
    "subhead":  (FONT_FAMILY, 14, "bold"),
    "body":     (FONT_FAMILY, 12),
    "body_bold":(FONT_FAMILY, 12, "bold"),
    "small":    (FONT_FAMILY, 10),
    "small_bold":(FONT_FAMILY, 10, "bold"),
    "micro":    (FONT_FAMILY, 9),
    "large":    (FONT_FAMILY, 32, "bold"),
    "hero":     (FONT_FAMILY, 48, "bold"),
}

APP_NAME   = "StudyNest"
APP_TAGLINE = "Your All-in-One Student Toolkit"

# CSV File Paths
CSV_DIR        = "data"
USERS_CSV      = os.path.join(CSV_DIR, "users.csv")
EXPENSES_CSV   = os.path.join(CSV_DIR, "expenses.csv")
STUDY_LOG_CSV  = os.path.join(CSV_DIR, "study_log.csv")

def ensure_data_dir():
    os.makedirs(CSV_DIR, exist_ok=True)
