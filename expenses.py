"""
expenses.py - Expense Tracker Logic (CSV-backed)
"""

import csv
import os
import datetime
from utils import (
    log_action, validate_input, catch_errors,
    validate_positive_float,
    EXPENSES_CSV, ensure_data_dir
)

EXPENSE_FIELDS = ["date", "username", "category", "description", "amount"]

CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Books & Stationery",
    "Entertainment",
    "Health",
    "Clothing",
    "Fees & Courses",
    "Other",
]


def _ensure_file():
    ensure_data_dir()
    if not os.path.exists(EXPENSES_CSV):
        with open(EXPENSES_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=EXPENSE_FIELDS).writeheader()


@log_action("Add Expense")
@catch_errors
def add_expense(username: str, category: str, description: str, amount: str) -> tuple[bool, str]:
    """
    Add an expense entry.
    Returns (success, message).
    """
    _ensure_file()
    try:
        amt = validate_positive_float(amount, "Amount")
    except ValueError as e:
        return False, str(e)

    if not description.strip():
        return False, "Description cannot be empty."
    if category not in CATEGORIES:
        return False, f"Invalid category: {category}"

    row = {
        "date":        datetime.date.today().isoformat(),
        "username":    username,
        "category":    category,
        "description": description.strip(),
        "amount":      f"{amt:.2f}",
    }
    with open(EXPENSES_CSV, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=EXPENSE_FIELDS).writerow(row)
    return True, f"Expense of ₹{amt:.2f} added successfully!"


@log_action("Load Expenses")
@catch_errors
def load_expenses(username: str) -> list[dict]:
    """Return list of expense dicts for the given user, newest first."""
    _ensure_file()
    rows = []
    with open(EXPENSES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["username"] == username:
                rows.append(row)
    return list(reversed(rows))


@log_action("Delete Expense")
@catch_errors
def delete_expense(username: str, target_row: dict) -> tuple[bool, str]:
    """Delete a specific expense row for the user."""
    _ensure_file()
    rows = []
    deleted = False
    with open(EXPENSES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (not deleted and row["username"] == username
                    and row == target_row):
                deleted = True
            else:
                rows.append(row)
    if not deleted:
        return False, "Record not found."
    with open(EXPENSES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPENSE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return True, "Expense deleted."


@catch_errors
def get_expense_summary(username: str) -> dict:
    """
    Returns summary dict:
    {total, count, average, by_category: {cat: total}, by_date: {date: total}}
    """
    rows = load_expenses(username)
    if not rows:
        return {"total": 0, "count": 0, "average": 0, "by_category": {}, "by_date": {}}

    total = 0.0
    by_cat: dict[str, float] = {}
    by_date: dict[str, float] = {}

    for row in rows:
        amt = float(row["amount"])
        total += amt
        by_cat[row["category"]] = by_cat.get(row["category"], 0) + amt
        by_date[row["date"]] = by_date.get(row["date"], 0) + amt

    return {
        "total":       total,
        "count":       len(rows),
        "average":     total / len(rows),
        "by_category": dict(sorted(by_cat.items(), key=lambda x: x[1], reverse=True)),
        "by_date":     dict(sorted(by_date.items())),
    }
