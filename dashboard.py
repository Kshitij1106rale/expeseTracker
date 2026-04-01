"""
dashboard.py - Dashboard UI component (rendered inside main app)
"""

import tkinter as tk
from tkinter import ttk
import datetime
from utils import THEME, FONTS, APP_NAME


def build_dashboard(parent_frame: tk.Frame, username: str,
                    expense_summary: dict, study_summary: dict,
                    on_navigate):
    """
    Render the dashboard inside `parent_frame`.
    `on_navigate(page_name)` switches to another page.
    """
    # Clear previous content
    for w in parent_frame.winfo_children():
        w.destroy()

    parent_frame.configure(bg=THEME["bg_dark"])

    # ── Header ───────────────────────────────────────────────────────────────
    header = tk.Frame(parent_frame, bg=THEME["bg_dark"])
    header.pack(fill="x", padx=30, pady=(30, 10))

    hour = datetime.datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

    tk.Label(
        header,
        text=f"{greeting}, {username.capitalize()}! 👋",
        font=FONTS["title"],
        fg=THEME["text_primary"],
        bg=THEME["bg_dark"],
    ).pack(anchor="w")

    tk.Label(
        header,
        text=f"📅  {datetime.date.today().strftime('%A, %d %B %Y')}",
        font=FONTS["body"],
        fg=THEME["text_secondary"],
        bg=THEME["bg_dark"],
    ).pack(anchor="w", pady=(4, 0))

    # ── Stat Cards ────────────────────────────────────────────────────────────
    cards_frame = tk.Frame(parent_frame, bg=THEME["bg_dark"])
    cards_frame.pack(fill="x", padx=30, pady=(20, 10))

    total_exp = expense_summary.get("total", 0)
    total_hrs = study_summary.get("total_hours", 0)
    streak     = study_summary.get("streak", 0)
    sessions   = study_summary.get("sessions", 0)

    stats = [
        ("💸", f"₹{total_exp:,.2f}", "Total Spent",      THEME["accent3"]),
        ("📚", f"{total_hrs:.1f} hrs", "Study Time",      THEME["accent"]),
        ("🔥", f"{streak} days",       "Study Streak",    THEME["accent5"]),
        ("📝", f"{sessions}",          "Study Sessions",  THEME["accent4"]),
    ]

    cards_frame.columnconfigure(tuple(range(len(stats))), weight=1)

    for col, (icon, value, label, color) in enumerate(stats):
        card = tk.Frame(cards_frame, bg=THEME["bg_card"],
                        highlightbackground=color,
                        highlightthickness=1,
                        padx=18, pady=18)
        card.grid(row=0, column=col, padx=8, sticky="ew")

        tk.Label(card, text=icon, font=(FONTS["heading"][0], 22),
                 bg=THEME["bg_card"], fg=color).pack(anchor="w")
        tk.Label(card, text=value, font=FONTS["heading"],
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w", pady=(4, 0))
        tk.Label(card, text=label, font=FONTS["small"],
                 bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(anchor="w")

    # ── Quick Actions ─────────────────────────────────────────────────────────
    tk.Label(
        parent_frame,
        text="⚡  Quick Actions",
        font=FONTS["subhead"],
        fg=THEME["text_primary"],
        bg=THEME["bg_dark"],
    ).pack(anchor="w", padx=30, pady=(28, 8))

    actions_frame = tk.Frame(parent_frame, bg=THEME["bg_dark"])
    actions_frame.pack(fill="x", padx=30)

    quick_actions = [
        ("➕  Add Expense",    "expenses",  THEME["accent3"]),
        ("📖  Log Study",      "study",     THEME["accent"]),
        ("📊  View Analysis",  "analyzer",  THEME["accent4"]),
    ]

    for i, (text, page, color) in enumerate(quick_actions):
        btn = tk.Button(
            actions_frame,
            text=text,
            font=FONTS["body_bold"],
            bg=color,
            fg=THEME["text_primary"],
            activebackground=THEME["hover"],
            activeforeground=THEME["text_primary"],
            relief="flat",
            padx=22,
            pady=12,
            cursor="hand2",
            command=lambda p=page: on_navigate(p),
            bd=0,
        )
        btn.grid(row=0, column=i, padx=(0 if i == 0 else 12, 0))
        _add_hover(btn, color, _lighten(color))

    # ── Recent Activity ───────────────────────────────────────────────────────
    tk.Label(
        parent_frame,
        text="🕒  Recent Activity",
        font=FONTS["subhead"],
        fg=THEME["text_primary"],
        bg=THEME["bg_dark"],
    ).pack(anchor="w", padx=30, pady=(28, 8))

    activity_frame = tk.Frame(parent_frame, bg=THEME["bg_card"],
                               highlightbackground=THEME["border"],
                               highlightthickness=1)
    activity_frame.pack(fill="x", padx=30, pady=(0, 30))

    # Show best subject & last category
    best_sub = study_summary.get("best_subject", "—")
    avg_hrs  = study_summary.get("avg_hours", 0)
    exp_cnt  = expense_summary.get("count", 0)
    exp_avg  = expense_summary.get("average", 0)

    items = [
        (THEME["accent"],  "🎓", f"Best Subject: {best_sub}",
         f"Avg session: {avg_hrs:.1f} hrs"),
        (THEME["accent3"], "💳", f"Expense Records: {exp_cnt}",
         f"Avg per entry: ₹{exp_avg:.2f}"),
    ]

    for i, (color, icon, title, sub) in enumerate(items):
        row_frame = tk.Frame(activity_frame, bg=THEME["bg_card"], pady=12, padx=16)
        row_frame.pack(fill="x")
        if i < len(items) - 1:
            tk.Frame(activity_frame, bg=THEME["border"], height=1).pack(fill="x")

        dot = tk.Frame(row_frame, bg=color, width=6, height=6)
        dot.pack(side="left", padx=(0, 12), pady=5)

        text_frame = tk.Frame(row_frame, bg=THEME["bg_card"])
        text_frame.pack(side="left")
        tk.Label(text_frame, text=f"{icon}  {title}", font=FONTS["body_bold"],
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(anchor="w")
        tk.Label(text_frame, text=sub, font=FONTS["small"],
                 fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack(anchor="w")


def _add_hover(widget, normal_color, hover_color):
    widget.bind("<Enter>", lambda e: widget.configure(bg=hover_color))
    widget.bind("<Leave>", lambda e: widget.configure(bg=normal_color))


def _lighten(hex_color: str) -> str:
    """Return a slightly lighter version of the hex color."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = min(255, r + 30)
    g = min(255, g + 30)
    b = min(255, b + 30)
    return f"#{r:02x}{g:02x}{b:02x}"
