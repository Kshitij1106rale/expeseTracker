"""
main.py - All-in-One Student Toolkit (StudyNest)
Entry point: runs the Tkinter application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from utils import THEME, FONTS, APP_NAME, APP_TAGLINE
from login import authenticate, register
from expenses import (add_expense, load_expenses, delete_expense,
                      get_expense_summary, CATEGORIES)
from study_log import (add_study_log, load_study_logs, delete_study_log,
                       get_study_summary, SUBJECTS, MOODS)
from dashboard import build_dashboard


# ══════════════════════════════════════════════════════════════════════════════
#  Helper Widgets
# ══════════════════════════════════════════════════════════════════════════════

def _configure_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background=THEME["bg_card"],
                    troughcolor=THEME["bg_dark"],
                    arrowcolor=THEME["text_secondary"],
                    bordercolor=THEME["border"],
                    lightcolor=THEME["bg_card"],
                    darkcolor=THEME["bg_card"])
    style.configure("TCombobox",
                    fieldbackground=THEME["bg_card"],
                    background=THEME["bg_card"],
                    foreground=THEME["text_primary"],
                    selectbackground=THEME["accent"],
                    selectforeground=THEME["text_primary"],
                    arrowcolor=THEME["accent"])
    style.map("TCombobox",
              fieldbackground=[("readonly", THEME["bg_card"])],
              foreground=[("readonly", THEME["text_primary"])])


def _label(parent, text, font=None, fg=None, bg=None, **kw):
    return tk.Label(
        parent, text=text,
        font=font or FONTS["body"],
        fg=fg or THEME["text_primary"],
        bg=bg or THEME["bg_dark"],
        **kw
    )


def _entry(parent, show=None, width=30):
    e = tk.Entry(
        parent,
        show=show,
        width=width,
        font=FONTS["body"],
        bg=THEME["bg_card"],
        fg=THEME["text_primary"],
        insertbackground=THEME["text_primary"],
        relief="flat",
        bd=0,
    )
    return e


def _btn(parent, text, command, color=None, fg=None, width=None, **kw):
    color = color or THEME["accent"]
    fg    = fg or THEME["text_primary"]
    b = tk.Button(
        parent, text=text, command=command,
        font=FONTS["body_bold"],
        bg=color, fg=fg,
        activebackground=_lighten(color),
        activeforeground=THEME["text_primary"],
        relief="flat", bd=0,
        padx=16, pady=9,
        cursor="hand2",
        width=width,
        **kw
    )
    b.bind("<Enter>", lambda e: b.configure(bg=_lighten(color)))
    b.bind("<Leave>", lambda e: b.configure(bg=color))
    return b


def _card_frame(parent, **kw):
    return tk.Frame(
        parent,
        bg=THEME["bg_card"],
        highlightbackground=THEME["border"],
        highlightthickness=1,
        **kw
    )


def _section_label(parent, text):
    tk.Label(
        parent, text=text,
        font=FONTS["subhead"],
        fg=THEME["text_primary"],
        bg=THEME["bg_dark"],
    ).pack(anchor="w", padx=30, pady=(20, 6))


def _lighten(hex_color: str) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r, g, b = min(255, r + 30), min(255, g + 30), min(255, b + 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def _entry_field(container, label_text, show=None, width=32):
    """Labeled entry with underline border effect."""
    frame = tk.Frame(container, bg=THEME["bg_dark"])
    tk.Label(frame, text=label_text, font=FONTS["small_bold"],
             fg=THEME["text_secondary"], bg=THEME["bg_dark"]).pack(anchor="w")
    wrapper = tk.Frame(frame, bg=THEME["bg_card"],
                       highlightbackground=THEME["border"],
                       highlightthickness=1)
    wrapper.pack(fill="x", pady=(3, 0))
    entry = tk.Entry(wrapper, show=show, width=width,
                     font=FONTS["body"],
                     bg=THEME["bg_card"],
                     fg=THEME["text_primary"],
                     insertbackground=THEME["accent"],
                     relief="flat", bd=8)
    entry.pack(fill="x")
    # focus highlight
    def on_focus_in(_):
        wrapper.configure(highlightbackground=THEME["accent"])
    def on_focus_out(_):
        wrapper.configure(highlightbackground=THEME["border"])
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return frame, entry


def _combo_field(container, label_text, values, width=29):
    frame = tk.Frame(container, bg=THEME["bg_dark"])
    tk.Label(frame, text=label_text, font=FONTS["small_bold"],
             fg=THEME["text_secondary"], bg=THEME["bg_dark"]).pack(anchor="w")
    var = tk.StringVar(value=values[0])
    combo = ttk.Combobox(frame, textvariable=var, values=values,
                         state="readonly", width=width, font=FONTS["body"])
    combo.pack(fill="x", pady=(3, 0))
    return frame, var


def _toast(root, message, color=None, duration=2500):
    """Show a temporary toast notification."""
    color = color or THEME["success"]
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.configure(bg=color)

    # Position bottom-right
    rx, ry = root.winfo_x(), root.winfo_y()
    rw, rh = root.winfo_width(), root.winfo_height()
    tw, th = 340, 50
    tx = rx + rw - tw - 20
    ty = ry + rh - th - 20
    toast.geometry(f"{tw}x{th}+{tx}+{ty}")
    toast.attributes("-topmost", True)

    tk.Label(toast, text=message, font=FONTS["body_bold"],
             fg=THEME["text_primary"], bg=color,
             wraplength=300, padx=12, pady=10).pack(expand=True)

    toast.after(duration, toast.destroy)


# ══════════════════════════════════════════════════════════════════════════════
#  Login / Register Window
# ══════════════════════════════════════════════════════════════════════════════

class LoginWindow:
    def __init__(self, root: tk.Tk, on_success):
        self.root       = root
        self.on_success = on_success
        self._mode      = "login"   # "login" or "register"
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self.root.configure(bg=THEME["bg_dark"])

        # Main container (centered)
        self.frame = tk.Frame(self.root, bg=THEME["bg_dark"])
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / App name
        tk.Label(self.frame, text="🎓", font=(FONTS["hero"][0], 54),
                 fg=THEME["accent"], bg=THEME["bg_dark"]).pack(pady=(0, 6))
        tk.Label(self.frame, text=APP_NAME, font=FONTS["title"],
                 fg=THEME["text_primary"], bg=THEME["bg_dark"]).pack()
        tk.Label(self.frame, text=APP_TAGLINE, font=FONTS["small"],
                 fg=THEME["text_secondary"], bg=THEME["bg_dark"]).pack(pady=(2, 24))

        # Card
        self.card = _card_frame(self.frame, padx=36, pady=30)
        self.card.pack(ipadx=4, ipady=4)

        # Mode title
        self.mode_label = tk.Label(
            self.card, text="Welcome Back",
            font=FONTS["heading"],
            fg=THEME["text_primary"],
            bg=THEME["bg_card"],
        )
        self.mode_label.pack(anchor="w", pady=(0, 18))

        # Username field
        uf, self.username_var = _entry_field(self.card, "USERNAME")
        uf.configure(bg=THEME["bg_card"])
        for child in uf.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=THEME["bg_card"])
        uf.pack(fill="x", pady=(0, 12))
        self.username_entry = uf.winfo_children()[1].winfo_children()[0]

        # Password field
        pf, self.password_var = _entry_field(self.card, "PASSWORD", show="●")
        pf.configure(bg=THEME["bg_card"])
        for child in pf.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=THEME["bg_card"])
        pf.pack(fill="x", pady=(0, 4))
        self.password_entry = pf.winfo_children()[1].winfo_children()[0]

        # Confirm password (registration only)
        self.confirm_frame, self.confirm_var = _entry_field(
            self.card, "CONFIRM PASSWORD", show="●")
        self.confirm_frame.configure(bg=THEME["bg_card"])
        for child in self.confirm_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=THEME["bg_card"])
        self.confirm_entry = (self.confirm_frame.winfo_children()[1]
                              .winfo_children()[0])
        # Hidden initially
        self.confirm_frame.pack_forget()

        # Status message
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(
            self.card, textvariable=self.status_var,
            font=FONTS["small"], fg=THEME["error"],
            bg=THEME["bg_card"], wraplength=280
        )
        self.status_lbl.pack(pady=(8, 0))

        # Action button
        self.action_btn = _btn(self.card, "Login", self._handle_action,
                               color=THEME["accent"])
        self.action_btn.pack(fill="x", pady=(14, 0))

        # Toggle mode link
        self.toggle_frame = tk.Frame(self.card, bg=THEME["bg_card"])
        self.toggle_frame.pack(pady=(12, 0))
        tk.Label(self.toggle_frame, text="Don't have an account?  ",
                 font=FONTS["small"], fg=THEME["text_secondary"],
                 bg=THEME["bg_card"]).pack(side="left")
        self.toggle_link = tk.Label(
            self.toggle_frame, text="Register",
            font=FONTS["small_bold"], fg=THEME["accent2"],
            bg=THEME["bg_card"], cursor="hand2"
        )
        self.toggle_link.pack(side="left")
        self.toggle_link.bind("<Button-1>", lambda e: self._toggle_mode())

        # Enter key binding
        self.root.bind("<Return>", lambda e: self._handle_action())

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _toggle_mode(self):
        self._mode = "register" if self._mode == "login" else "login"
        if self._mode == "register":
            self.mode_label.configure(text="Create Account")
            self.action_btn.configure(text="Register")
            self.confirm_frame.configure(bg=THEME["bg_card"])
            self.confirm_frame.pack(fill="x", pady=(0, 4))
            # Reorder: confirm before status
            self.confirm_frame.pack(before=self.status_lbl, fill="x", pady=(0, 4))
            self.toggle_link.configure(text="Login instead")
            for lbl in self.toggle_frame.winfo_children():
                if isinstance(lbl, tk.Label) and lbl != self.toggle_link:
                    lbl.configure(text="Already have an account?  ")
        else:
            self.mode_label.configure(text="Welcome Back")
            self.action_btn.configure(text="Login")
            self.confirm_frame.pack_forget()
            self.toggle_link.configure(text="Register")
            for lbl in self.toggle_frame.winfo_children():
                if isinstance(lbl, tk.Label) and lbl != self.toggle_link:
                    lbl.configure(text="Don't have an account?  ")
        self.status_var.set("")

    def _handle_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self._mode == "login":
            try:
                ok = authenticate(username, password)
            except ValueError as e:
                self.status_var.set(str(e))
                self.status_lbl.configure(fg=THEME["error"])
                return
            if ok:
                self.status_var.set("")
                self.on_success(username)
            else:
                self.status_var.set("❌  Invalid username or password.")
                self.status_lbl.configure(fg=THEME["error"])

        else:  # register
            confirm = self.confirm_entry.get()
            if password != confirm:
                self.status_var.set("❌  Passwords do not match.")
                self.status_lbl.configure(fg=THEME["error"])
                return
            ok, msg = register(username, password)
            if ok:
                self.status_var.set(f"✅  {msg}")
                self.status_lbl.configure(fg=THEME["success"])
                self._toggle_mode()
            else:
                self.status_var.set(f"❌  {msg}")
                self.status_lbl.configure(fg=THEME["error"])


# ══════════════════════════════════════════════════════════════════════════════
#  Main Application Window
# ══════════════════════════════════════════════════════════════════════════════

class StudentToolkitApp:
    PAGES = ["dashboard", "expenses", "study", "analyzer"]
    PAGE_ICONS = {
        "dashboard": "🏠",
        "expenses":  "💸",
        "study":     "📚",
        "analyzer":  "📊",
    }
    PAGE_LABELS = {
        "dashboard": "Dashboard",
        "expenses":  "Expenses",
        "study":     "Study Log",
        "analyzer":  "Analyzer",
    }

    def __init__(self, root: tk.Tk, username: str):
        self.root     = root
        self.username = username
        self._current_page = None
        self._build()
        self.navigate("dashboard")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self.root.configure(bg=THEME["bg_dark"])

        # ── Sidebar ──────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=THEME["bg_sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App brand
        brand = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"])
        brand.pack(fill="x", padx=20, pady=(26, 30))
        tk.Label(brand, text="🎓", font=(FONTS["heading"][0], 26),
                 fg=THEME["accent"], bg=THEME["bg_sidebar"]).pack(side="left")
        tk.Label(brand, text=f"  {APP_NAME}", font=FONTS["subhead"],
                 fg=THEME["text_primary"], bg=THEME["bg_sidebar"]).pack(side="left")

        # Nav buttons
        self._nav_btns: dict[str, tk.Frame] = {}
        for page in self.PAGES:
            self._nav_btns[page] = self._make_nav_btn(page)

        # Spacer
        tk.Frame(self.sidebar, bg=THEME["bg_sidebar"]).pack(expand=True, fill="y")

        # User info panel at bottom
        user_panel = tk.Frame(self.sidebar, bg=THEME["bg_card"],
                              padx=16, pady=14)
        user_panel.pack(fill="x", side="bottom", padx=10, pady=14)
        tk.Label(user_panel, text="👤  " + self.username.capitalize(),
                 font=FONTS["body_bold"],
                 fg=THEME["text_primary"],
                 bg=THEME["bg_card"]).pack(anchor="w")
        tk.Label(user_panel, text="Student",
                 font=FONTS["small"],
                 fg=THEME["text_secondary"],
                 bg=THEME["bg_card"]).pack(anchor="w")
        _btn(user_panel, "Logout", self._logout,
             color=THEME["error"]).pack(fill="x", pady=(10, 0))

        # ── Content area ─────────────────────────────────────────────────────
        self.content = tk.Frame(self.root, bg=THEME["bg_dark"])
        self.content.pack(side="right", fill="both", expand=True)

    def _make_nav_btn(self, page: str) -> tk.Frame:
        frame = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"],
                         cursor="hand2")
        frame.pack(fill="x", padx=10, pady=2)

        icon  = self.PAGE_ICONS[page]
        label = self.PAGE_LABELS[page]

        inner = tk.Frame(frame, bg=THEME["bg_sidebar"], padx=14, pady=10)
        inner.pack(fill="x")

        ico_lbl = tk.Label(inner, text=icon + "  " + label,
                           font=FONTS["body"],
                           fg=THEME["text_secondary"],
                           bg=THEME["bg_sidebar"],
                           anchor="w")
        ico_lbl.pack(fill="x")

        def enter(_):
            if self._current_page != page:
                frame.configure(bg=THEME["hover"])
                inner.configure(bg=THEME["hover"])
                ico_lbl.configure(bg=THEME["hover"])

        def leave(_):
            if self._current_page != page:
                frame.configure(bg=THEME["bg_sidebar"])
                inner.configure(bg=THEME["bg_sidebar"])
                ico_lbl.configure(bg=THEME["bg_sidebar"])

        frame.bind("<Button-1>", lambda e: self.navigate(page))
        inner.bind("<Button-1>", lambda e: self.navigate(page))
        ico_lbl.bind("<Button-1>", lambda e: self.navigate(page))
        frame.bind("<Enter>", enter)
        frame.bind("<Leave>", leave)
        inner.bind("<Enter>", enter)
        inner.bind("<Leave>", leave)
        ico_lbl.bind("<Enter>", enter)
        ico_lbl.bind("<Leave>", leave)

        # Store sub-widgets for highlight
        frame._inner   = inner
        frame._lbl     = ico_lbl
        return frame

    def _highlight_nav(self, active_page: str):
        for page, frame in self._nav_btns.items():
            inner = frame._inner
            lbl   = frame._lbl
            if page == active_page:
                frame.configure(bg=THEME["accent"])
                inner.configure(bg=THEME["accent"])
                lbl.configure(bg=THEME["accent"],
                               fg=THEME["text_primary"],
                               font=FONTS["body_bold"])
            else:
                frame.configure(bg=THEME["bg_sidebar"])
                inner.configure(bg=THEME["bg_sidebar"])
                lbl.configure(bg=THEME["bg_sidebar"],
                               fg=THEME["text_secondary"],
                               font=FONTS["body"])

    # ── Navigation ────────────────────────────────────────────────────────────
    def navigate(self, page: str):
        self._current_page = page
        self._highlight_nav(page)

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        getattr(self, f"_page_{page}")()

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _page_dashboard(self):
        exp_sum   = get_expense_summary(self.username)
        study_sum = get_study_summary(self.username)

        canvas, scrollable = self._scrollable_frame(self.content)
        build_dashboard(scrollable, self.username,
                        exp_sum, study_sum,
                        self.navigate)

    # ── EXPENSES PAGE ─────────────────────────────────────────────────────────
    def _page_expenses(self):
        canvas, scrollable = self._scrollable_frame(self.content)
        scrollable.configure(bg=THEME["bg_dark"])

        # Header
        hdr = tk.Frame(scrollable, bg=THEME["bg_dark"])
        hdr.pack(fill="x", padx=30, pady=(28, 4))
        tk.Label(hdr, text="💸  Expense Tracker",
                 font=FONTS["heading"],
                 fg=THEME["text_primary"],
                 bg=THEME["bg_dark"]).pack(side="left")

        # Summary strip
        summary = get_expense_summary(self.username)
        strip = tk.Frame(scrollable, bg=THEME["bg_card"],
                         highlightbackground=THEME["border"],
                         highlightthickness=1)
        strip.pack(fill="x", padx=30, pady=(0, 18))

        for col, (title, value) in enumerate([
            ("Total Spent",  f"₹{summary['total']:,.2f}"),
            ("Entries",      str(summary["count"])),
            ("Average",      f"₹{summary['average']:,.2f}"),
        ]):
            cell = tk.Frame(strip, bg=THEME["bg_card"], padx=24, pady=14)
            cell.grid(row=0, column=col, sticky="ew")
            strip.columnconfigure(col, weight=1)
            if col > 0:
                tk.Frame(strip, bg=THEME["border"], width=1).grid(
                    row=0, column=col * 2 - 1, sticky="ns")
            tk.Label(cell, text=value, font=FONTS["heading"],
                     fg=THEME["accent3"], bg=THEME["bg_card"]).pack()
            tk.Label(cell, text=title, font=FONTS["small"],
                     fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack()

        # Add expense form
        _section_label(scrollable, "➕  Add New Expense")
        form_card = _card_frame(scrollable, padx=24, pady=20)
        form_card.pack(fill="x", padx=30)

        # Category
        cf, cat_var = _combo_field(form_card, "CATEGORY", CATEGORIES, width=36)
        cf.configure(bg=THEME["bg_card"])
        for c in cf.winfo_children():
            if isinstance(c, tk.Label):
                c.configure(bg=THEME["bg_card"])
        cf.pack(fill="x", pady=(0, 12))

        # Description
        df, desc_frame_ref = _entry_field(form_card, "DESCRIPTION", width=38)
        df.configure(bg=THEME["bg_card"])
        for c in df.winfo_children():
            if isinstance(c, tk.Label):
                c.configure(bg=THEME["bg_card"])
        df.pack(fill="x", pady=(0, 12))
        desc_entry = df.winfo_children()[1].winfo_children()[0]

        # Amount
        af, amt_frame_ref = _entry_field(form_card, "AMOUNT (₹)", width=38)
        af.configure(bg=THEME["bg_card"])
        for c in af.winfo_children():
            if isinstance(c, tk.Label):
                c.configure(bg=THEME["bg_card"])
        af.pack(fill="x", pady=(0, 16))
        amt_entry = af.winfo_children()[1].winfo_children()[0]

        status_var = tk.StringVar()
        status_lbl = tk.Label(form_card, textvariable=status_var,
                               font=FONTS["small"], bg=THEME["bg_card"],
                               fg=THEME["success"])
        status_lbl.pack(anchor="w", pady=(0, 8))

        def submit_expense():
            ok, msg = add_expense(
                self.username, cat_var.get(),
                desc_entry.get(), amt_entry.get()
            )
            if ok:
                status_var.set(f"✅  {msg}")
                status_lbl.configure(fg=THEME["success"])
                desc_entry.delete(0, tk.END)
                amt_entry.delete(0, tk.END)
                _toast(self.root, msg)
                self._page_expenses()   # refresh
            else:
                status_var.set(f"❌  {msg}")
                status_lbl.configure(fg=THEME["error"])

        _btn(form_card, "Add Expense", submit_expense,
             color=THEME["accent3"]).pack(anchor="w")

        # Expense list
        _section_label(scrollable, "📋  Recent Expenses")
        self._expense_list(scrollable)

    def _expense_list(self, parent):
        rows = load_expenses(self.username)
        if not rows:
            _card_frame(parent, padx=24, pady=20).pack(fill="x", padx=30)
            tk.Label(parent.winfo_children()[-1],
                     text="No expenses recorded yet.",
                     font=FONTS["body"],
                     fg=THEME["text_secondary"],
                     bg=THEME["bg_card"]).pack()
            return

        list_card = _card_frame(parent)
        list_card.pack(fill="x", padx=30, pady=(0, 30))

        # Header row
        header = tk.Frame(list_card, bg=THEME["border"])
        header.pack(fill="x")
        for col_text, col_weight in [
            ("Date", 2), ("Category", 3), ("Description", 4), ("Amount", 2), ("", 1)
        ]:
            tk.Label(header, text=col_text, font=FONTS["small_bold"],
                     fg=THEME["text_secondary"], bg=THEME["border"],
                     padx=12, pady=8, anchor="w").pack(side="left",
                                                        expand=(col_weight > 1),
                                                        fill="x")

        color_map = {}
        for i, row in enumerate(rows):
            bg = THEME["bg_card"] if i % 2 == 0 else THEME["bg_dark"]
            row_frame = tk.Frame(list_card, bg=bg)
            row_frame.pack(fill="x")

            # Amount color
            amt = float(row["amount"])
            amt_color = (THEME["accent3"] if amt >= 500
                         else THEME["accent4"] if amt >= 100
                         else THEME["text_primary"])

            for text, expand, anchor in [
                (row["date"], False, "w"),
                (row["category"], True, "w"),
                (row["description"], True, "w"),
            ]:
                tk.Label(row_frame, text=text, font=FONTS["small"],
                         fg=THEME["text_primary"], bg=bg,
                         padx=12, pady=8, anchor=anchor
                         ).pack(side="left", expand=expand, fill="x")

            tk.Label(row_frame, text=f"₹{amt:.2f}",
                     font=FONTS["small_bold"], fg=amt_color,
                     bg=bg, padx=12, pady=8, anchor="w"
                     ).pack(side="left", fill="x")

            def make_del(r=row):
                def _del():
                    ok, msg = delete_expense(self.username, r)
                    if ok:
                        _toast(self.root, "Expense deleted.", THEME["warning"])
                        self._page_expenses()
                    else:
                        _toast(self.root, msg, THEME["error"])
                return _del

            tk.Button(row_frame, text="✕", font=FONTS["small_bold"],
                      bg=bg, fg=THEME["error"],
                      activebackground=THEME["error"],
                      activeforeground=THEME["text_primary"],
                      relief="flat", bd=0, padx=8, pady=8,
                      cursor="hand2",
                      command=make_del()).pack(side="right")

    # ── STUDY LOG PAGE ────────────────────────────────────────────────────────
    def _page_study(self):
        canvas, scrollable = self._scrollable_frame(self.content)
        scrollable.configure(bg=THEME["bg_dark"])

        # Header
        hdr = tk.Frame(scrollable, bg=THEME["bg_dark"])
        hdr.pack(fill="x", padx=30, pady=(28, 4))
        tk.Label(hdr, text="📚  Study Log",
                 font=FONTS["heading"],
                 fg=THEME["text_primary"],
                 bg=THEME["bg_dark"]).pack(side="left")

        # Summary strip
        summary = get_study_summary(self.username)
        strip = tk.Frame(scrollable, bg=THEME["bg_card"],
                         highlightbackground=THEME["border"],
                         highlightthickness=1)
        strip.pack(fill="x", padx=30, pady=(0, 18))

        for col, (title, value) in enumerate([
            ("Total Hours",   f"{summary['total_hours']:.1f} hrs"),
            ("Sessions",      str(summary["sessions"])),
            ("Daily Average", f"{summary['avg_hours']:.1f} hrs"),
            ("Study Streak",  f"🔥 {summary['streak']} days"),
        ]):
            cell = tk.Frame(strip, bg=THEME["bg_card"], padx=20, pady=14)
            cell.grid(row=0, column=col, sticky="ew")
            strip.columnconfigure(col, weight=1)
            if col > 0:
                tk.Frame(strip, bg=THEME["border"], width=1).grid(
                    row=0, column=col * 2 - 1, sticky="ns")
            tk.Label(cell, text=value, font=FONTS["heading"],
                     fg=THEME["accent"], bg=THEME["bg_card"]).pack()
            tk.Label(cell, text=title, font=FONTS["small"],
                     fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack()

        # Log form
        _section_label(scrollable, "➕  Log Study Session")
        form_card = _card_frame(scrollable, padx=24, pady=20)
        form_card.pack(fill="x", padx=30)

        left = tk.Frame(form_card, bg=THEME["bg_card"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))
        right = tk.Frame(form_card, bg=THEME["bg_card"])
        right.pack(side="left", fill="both", expand=True)

        # Subject
        sf, sub_var = _combo_field(left, "SUBJECT", SUBJECTS, width=26)
        sf.configure(bg=THEME["bg_card"])
        for c in sf.winfo_children():
            if isinstance(c, tk.Label): c.configure(bg=THEME["bg_card"])
        sf.pack(fill="x", pady=(0, 12))

        # Mood
        mf, mood_var = _combo_field(left, "MOOD", MOODS, width=26)
        mf.configure(bg=THEME["bg_card"])
        for c in mf.winfo_children():
            if isinstance(c, tk.Label): c.configure(bg=THEME["bg_card"])
        mf.pack(fill="x")

        # Hours
        hf, hrs_frame = _entry_field(right, "STUDY HOURS", width=24)
        hf.configure(bg=THEME["bg_card"])
        for c in hf.winfo_children():
            if isinstance(c, tk.Label): c.configure(bg=THEME["bg_card"])
        hf.pack(fill="x", pady=(0, 12))
        hrs_entry = hf.winfo_children()[1].winfo_children()[0]

        # Notes
        nf, notes_frame = _entry_field(right, "NOTES (optional)", width=24)
        nf.configure(bg=THEME["bg_card"])
        for c in nf.winfo_children():
            if isinstance(c, tk.Label): c.configure(bg=THEME["bg_card"])
        nf.pack(fill="x")
        notes_entry = nf.winfo_children()[1].winfo_children()[0]

        status_var = tk.StringVar()
        status_lbl = tk.Label(form_card, textvariable=status_var,
                               font=FONTS["small"], bg=THEME["bg_card"],
                               fg=THEME["success"])
        status_lbl.pack(anchor="w", pady=(12, 6))

        def submit_log():
            ok, msg = add_study_log(
                self.username, sub_var.get(), hrs_entry.get(),
                notes_entry.get(), mood_var.get()
            )
            if ok:
                status_var.set(f"✅  {msg}")
                status_lbl.configure(fg=THEME["success"])
                hrs_entry.delete(0, tk.END)
                notes_entry.delete(0, tk.END)
                _toast(self.root, msg)
                self._page_study()
            else:
                status_var.set(f"❌  {msg}")
                status_lbl.configure(fg=THEME["error"])

        _btn(form_card, "Log Session", submit_log,
             color=THEME["accent"]).pack(anchor="w")

        # Study log list
        _section_label(scrollable, "📋  Study History")
        self._study_list(scrollable)

    def _study_list(self, parent):
        rows = load_study_logs(self.username)
        if not rows:
            c = _card_frame(parent, padx=24, pady=20)
            c.pack(fill="x", padx=30)
            tk.Label(c, text="No study sessions recorded yet.",
                     font=FONTS["body"],
                     fg=THEME["text_secondary"],
                     bg=THEME["bg_card"]).pack()
            return

        list_card = _card_frame(parent)
        list_card.pack(fill="x", padx=30, pady=(0, 30))

        header = tk.Frame(list_card, bg=THEME["border"])
        header.pack(fill="x")
        for text in ["Date", "Subject", "Hours", "Mood", "Notes", ""]:
            tk.Label(header, text=text, font=FONTS["small_bold"],
                     fg=THEME["text_secondary"], bg=THEME["border"],
                     padx=12, pady=8, anchor="w").pack(side="left", expand=True, fill="x")

        for i, row in enumerate(rows):
            bg = THEME["bg_card"] if i % 2 == 0 else THEME["bg_dark"]
            row_frame = tk.Frame(list_card, bg=bg)
            row_frame.pack(fill="x")

            hrs = float(row["hours"])
            hrs_color = (THEME["accent5"] if hrs >= 4
                         else THEME["accent4"] if hrs >= 2
                         else THEME["text_primary"])

            for text, expand in [
                (row["date"], True),
                (row["subject"], True),
            ]:
                tk.Label(row_frame, text=text, font=FONTS["small"],
                         fg=THEME["text_primary"], bg=bg,
                         padx=12, pady=8, anchor="w"
                         ).pack(side="left", expand=expand, fill="x")

            tk.Label(row_frame, text=f"{hrs:.1f} hrs",
                     font=FONTS["small_bold"], fg=hrs_color,
                     bg=bg, padx=12, pady=8, anchor="w"
                     ).pack(side="left", fill="x")

            for text, expand in [
                (row["mood"], True),
                (row["notes"][:28] + "…" if len(row["notes"]) > 28
                 else row["notes"], True),
            ]:
                tk.Label(row_frame, text=text, font=FONTS["small"],
                         fg=THEME["text_primary"], bg=bg,
                         padx=12, pady=8, anchor="w"
                         ).pack(side="left", expand=expand, fill="x")

            def make_del(r=row):
                def _del():
                    ok, msg = delete_study_log(self.username, r)
                    if ok:
                        _toast(self.root, "Study log deleted.", THEME["warning"])
                        self._page_study()
                    else:
                        _toast(self.root, msg, THEME["error"])
                return _del

            tk.Button(row_frame, text="✕", font=FONTS["small_bold"],
                      bg=bg, fg=THEME["error"],
                      activebackground=THEME["error"],
                      activeforeground=THEME["text_primary"],
                      relief="flat", bd=0, padx=8, pady=8,
                      cursor="hand2",
                      command=make_del()).pack(side="right")

    # ── ANALYZER PAGE ─────────────────────────────────────────────────────────
    def _page_analyzer(self):
        canvas, scrollable = self._scrollable_frame(self.content)
        scrollable.configure(bg=THEME["bg_dark"])

        tk.Label(scrollable, text="📊  Data Analyzer",
                 font=FONTS["heading"],
                 fg=THEME["text_primary"],
                 bg=THEME["bg_dark"]).pack(anchor="w", padx=30, pady=(28, 4))
        tk.Label(scrollable,
                 text="Insights from your expenses and study patterns",
                 font=FONTS["body"],
                 fg=THEME["text_secondary"],
                 bg=THEME["bg_dark"]).pack(anchor="w", padx=30, pady=(0, 20))

        exp_sum   = get_expense_summary(self.username)
        study_sum = get_study_summary(self.username)

        # ── Expense Analysis ──────────────────────────────────────────────────
        _section_label(scrollable, "💸  Expense Breakdown by Category")
        if exp_sum["by_category"]:
            by_cat = exp_sum["by_category"]
            total  = exp_sum["total"]
            self._bar_chart(scrollable, by_cat, total, THEME["accent3"], "₹")
        else:
            self._empty_state(scrollable, "No expense data yet.")

        # ── Study Analysis ────────────────────────────────────────────────────
        _section_label(scrollable, "📚  Study Hours by Subject")
        if study_sum["by_subject"]:
            by_sub = study_sum["by_subject"]
            total  = study_sum["total_hours"]
            self._bar_chart(scrollable, by_sub, total, THEME["accent"], "hrs")
        else:
            self._empty_state(scrollable, "No study data yet.")

        # ── Combined Insights ─────────────────────────────────────────────────
        _section_label(scrollable, "🧠  Key Insights")
        insights_card = _card_frame(scrollable, padx=24, pady=20)
        insights_card.pack(fill="x", padx=30, pady=(0, 30))

        insights = self._generate_insights(exp_sum, study_sum)
        for i, insight in enumerate(insights):
            bullet = tk.Frame(insights_card, bg=THEME["bg_card"])
            bullet.pack(fill="x", pady=4)
            dot = tk.Frame(bullet, bg=THEME["accent"], width=8, height=8)
            dot.pack(side="left", padx=(0, 10), pady=4)
            tk.Label(bullet, text=insight,
                     font=FONTS["body"],
                     fg=THEME["text_primary"],
                     bg=THEME["bg_card"],
                     anchor="w",
                     wraplength=560).pack(side="left", fill="x", expand=True)

    def _bar_chart(self, parent, data: dict, total: float,
                   color: str, unit: str):
        """Render a simple horizontal bar chart."""
        chart_card = _card_frame(parent, padx=24, pady=20)
        chart_card.pack(fill="x", padx=30, pady=(0, 10))

        max_val = max(data.values()) if data else 1
        for label, value in data.items():
            row = tk.Frame(chart_card, bg=THEME["bg_card"])
            row.pack(fill="x", pady=4)

            # Label
            tk.Label(row, text=label, font=FONTS["small"],
                     fg=THEME["text_primary"], bg=THEME["bg_card"],
                     width=22, anchor="w").pack(side="left")

            # Bar container
            bar_bg = tk.Frame(row, bg=THEME["border"], height=18)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(6, 10))
            bar_bg.update_idletasks()

            pct = value / max_val if max_val else 0
            bar_fill = tk.Frame(bar_bg, bg=color, height=18)
            bar_fill.place(x=0, y=0, relwidth=pct, relheight=1)

            # Value
            pct_total = (value / total * 100) if total else 0
            tk.Label(row,
                     text=f"{unit}{value:.1f}  ({pct_total:.0f}%)",
                     font=FONTS["small_bold"],
                     fg=color, bg=THEME["bg_card"],
                     width=16, anchor="w").pack(side="left")

    def _empty_state(self, parent, message: str):
        c = _card_frame(parent, padx=24, pady=20)
        c.pack(fill="x", padx=30)
        tk.Label(c, text=message, font=FONTS["body"],
                 fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack()

    def _generate_insights(self, exp: dict, study: dict) -> list[str]:
        insights = []
        if exp["count"] > 0:
            by_cat = exp["by_category"]
            top_cat = list(by_cat.keys())[0] if by_cat else "N/A"
            insights.append(
                f"💰 Your biggest expense category is '{top_cat}' "
                f"(₹{by_cat.get(top_cat, 0):.2f} total)."
            )
            insights.append(
                f"📈 You have logged {exp['count']} expense entries "
                f"with an average of ₹{exp['average']:.2f} per entry."
            )
        if study["sessions"] > 0:
            insights.append(
                f"🎓 Your most studied subject is '{study['best_subject']}' "
                f"— keep it up!"
            )
            insights.append(
                f"⏱️ You have studied for {study['total_hours']:.1f} hours "
                f"across {study['sessions']} session(s), "
                f"averaging {study['avg_hours']:.1f} hrs/session."
            )
            if study["streak"] >= 3:
                insights.append(
                    f"🔥 Amazing! You are on a {study['streak']}-day study streak!"
                )
            elif study["streak"] > 0:
                insights.append(
                    f"✅ You have a {study['streak']}-day study streak. Keep going!"
                )
        if not insights:
            insights.append("Start adding expenses and study logs to see insights here!")
        return insights

    # ── Utilities ─────────────────────────────────────────────────────────────
    def _scrollable_frame(self, parent) -> tuple[tk.Canvas, tk.Frame]:
        """Return (canvas, inner_frame) with vertical scrollbar."""
        outer = tk.Frame(parent, bg=THEME["bg_dark"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=THEME["bg_dark"],
                           highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical",
                                  command=canvas.yview)

        scrollable = tk.Frame(canvas, bg=THEME["bg_dark"])
        win_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(event):
            canvas.itemconfig(win_id, width=event.width)

        scrollable.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_resize)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        return canvas, scrollable

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?",
                                icon="question"):
            self.root.destroy()
            _run_app()


# ══════════════════════════════════════════════════════════════════════════════
#  Bootstrap
# ══════════════════════════════════════════════════════════════════════════════

def _run_app():
    root = tk.Tk()
    root.title(f"{APP_NAME} — {APP_TAGLINE}")
    root.geometry("1100x700")
    root.minsize(900, 600)
    _configure_style()

    # Center window
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x  = (sw - 1100) // 2
    y  = (sh - 700)  // 2
    root.geometry(f"1100x700+{x}+{y}")

    # Login flow
    login_win = [None]

    def on_login_success(username: str):
        # Destroy login widgets
        for w in root.winfo_children():
            w.destroy()
        StudentToolkitApp(root, username)

    login_win[0] = LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    _run_app()
