"""
study_log.py - Study Log Logic (CSV-backed)
"""

import csv
import os
import datetime
from utils import (
    log_action, validate_input, catch_errors,
    validate_positive_float,
    STUDY_LOG_CSV, ensure_data_dir
)

STUDY_FIELDS = ["date", "username", "subject", "hours", "notes", "mood"]

SUBJECTS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "English",
    "History",
    "Geography",
    "Economics",
    "Other",
]

MOODS = ["😊 Focused", "😐 Okay", "😴 Tired", "😤 Stressed", "🔥 Productive"]


def _ensure_file():
    ensure_data_dir()
    if not os.path.exists(STUDY_LOG_CSV):
        with open(STUDY_LOG_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=STUDY_FIELDS).writeheader()


@log_action("Add Study Log")
@catch_errors
def add_study_log(username: str, subject: str, hours: str,
                  notes: str, mood: str) -> tuple[bool, str]:
    """
    Add a study session.
    Returns (success, message).
    """
    _ensure_file()
    try:
        hrs = validate_positive_float(hours, "Study hours")
    except ValueError as e:
        return False, str(e)

    if hrs > 24:
        return False, "Study hours cannot exceed 24 in a day."
    if subject not in SUBJECTS:
        return False, f"Invalid subject: {subject}"
    if mood not in MOODS:
        mood = MOODS[0]

    row = {
        "date":     datetime.date.today().isoformat(),
        "username": username,
        "subject":  subject,
        "hours":    f"{hrs:.1f}",
        "notes":    notes.strip(),
        "mood":     mood,
    }
    with open(STUDY_LOG_CSV, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=STUDY_FIELDS).writerow(row)
    return True, f"Study session of {hrs:.1f} hrs logged for {subject}!"


@log_action("Load Study Log")
@catch_errors
def load_study_logs(username: str) -> list[dict]:
    """Return list of study log dicts for the user, newest first."""
    _ensure_file()
    rows = []
    with open(STUDY_LOG_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["username"] == username:
                rows.append(row)
    return list(reversed(rows))


@log_action("Delete Study Log")
@catch_errors
def delete_study_log(username: str, target_row: dict) -> tuple[bool, str]:
    """Delete a specific study log row for the user."""
    _ensure_file()
    rows = []
    deleted = False
    with open(STUDY_LOG_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (not deleted and row["username"] == username
                    and row == target_row):
                deleted = True
            else:
                rows.append(row)
    if not deleted:
        return False, "Record not found."
    with open(STUDY_LOG_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STUDY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return True, "Study log deleted."


@catch_errors
def get_study_summary(username: str) -> dict:
    """
    Returns summary dict:
    {total_hours, sessions, avg_hours, by_subject: {sub: hrs},
     by_date: {date: hrs}, streak: int, best_subject: str}
    """
    rows = load_study_logs(username)
    if not rows:
        return {
            "total_hours": 0, "sessions": 0, "avg_hours": 0,
            "by_subject": {}, "by_date": {}, "streak": 0, "best_subject": "—"
        }

    total = 0.0
    by_sub: dict[str, float] = {}
    by_date: dict[str, float] = {}

    for row in rows:
        hrs = float(row["hours"])
        total += hrs
        by_sub[row["subject"]] = by_sub.get(row["subject"], 0) + hrs
        by_date[row["date"]] = by_date.get(row["date"], 0) + hrs

    # Streak calculation (consecutive days with study)
    sorted_dates = sorted(by_date.keys(), reverse=True)
    streak = 0
    check = datetime.date.today()
    for d in sorted_dates:
        if datetime.date.fromisoformat(d) == check:
            streak += 1
            check -= datetime.timedelta(days=1)
        else:
            break

    best_subject = max(by_sub, key=by_sub.get) if by_sub else "—"

    return {
        "total_hours":  total,
        "sessions":     len(rows),
        "avg_hours":    total / len(rows),
        "by_subject":   dict(sorted(by_sub.items(), key=lambda x: x[1], reverse=True)),
        "by_date":      dict(sorted(by_date.items())),
        "streak":       streak,
        "best_subject": best_subject,
    }
