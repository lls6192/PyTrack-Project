"""
PyTrack UI theme.
Centralizes colors, fonts, and reusable styling helpers so the visual
language stays consistent across pages without changing any app logic.

Usage:
    from theme import apply_theme, fonts, COLORS, style_primary_button, ...
    fonts_dict = apply_theme(root)   # call once on the Tk root
"""

from tkinter import ttk
from tkinter import font as tkfont


# ---------------------------------------------------------------- COLORS ----
COLORS = {
    # surfaces
    "bg_main":        "#F7F4EE",   # warm paper cream (app background)
    "bg_card":        "#FFFFFF",   # cards / panels
    "bg_subtle":      "#FBF9F4",   # alt rows, soft sections
    "bg_header":      "#F0EBDF",   # treeview header / tag bars
    "border":         "#E5DED1",   # quiet borders
    "divider":        "#EFEAE0",

    # text
    "text_primary":   "#2B2620",   # near-black warm
    "text_secondary": "#857C70",   # body / labels
    "text_muted":     "#A8A095",
    "text_invert":    "#FFFFFF",

    # accent (deep forest)
    "accent":         "#3A5A40",
    "accent_hover":   "#2D4733",
    "accent_soft":    "#E8EFE9",   # tint backgrounds

    # status
    "danger":         "#A8503D",
    "danger_hover":   "#8C3F2E",
    "warning":        "#C4994A",
    "success":        "#3A5A40",
}


# ----------------------------------------------------------------- FONTS ----
# fonts dict gets populated by apply_theme(); other modules import it after.
fonts = {}


def _pick(preferred, fallback="Helvetica"):
    """Return the first font family available on this system, else fallback."""
    available = set(tkfont.families())
    for name in preferred:
        if name in available:
            return name
    return fallback


def _build_fonts():
    serif = _pick(["Georgia", "Cambria", "Times New Roman"], "Times")
    sans  = _pick(["Segoe UI", "Helvetica Neue", "Helvetica", "Arial"], "Helvetica")

    return {
        "title":       tkfont.Font(family=serif, size=26, weight="bold"),
        "subtitle":    tkfont.Font(family=serif, size=12, slant="italic"),
        "heading":     tkfont.Font(family=serif, size=15, weight="bold"),
        "section":     tkfont.Font(family=sans,  size=10, weight="bold"),
        "body":        tkfont.Font(family=sans,  size=11),
        "body_bold":   tkfont.Font(family=sans,  size=11, weight="bold"),
        "small":       tkfont.Font(family=sans,  size=10),
        "small_muted": tkfont.Font(family=sans,  size=9),
        "button":      tkfont.Font(family=sans,  size=10, weight="bold"),
        "report":      tkfont.Font(family=serif, size=12),
        "report_bold": tkfont.Font(family=serif, size=14, weight="bold"),
        "_serif":      serif,
        "_sans":       sans,
    }


# ----------------------------------------------------------- THEME SETUP ----
def apply_theme(root):
    """Apply the global theme to a Tk root. Returns the fonts dict."""
    global fonts
    fonts.update(_build_fonts())
    root.configure(bg=COLORS["bg_main"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")   # most flexible for color overrides
    except Exception:
        pass

    # ttk.Frame
    style.configure("TFrame", background=COLORS["bg_main"])
    style.configure(
        "Card.TFrame",
        background=COLORS["bg_card"],
        relief="flat",
        borderwidth=0,
    )

    # ttk.Combobox
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["bg_card"],
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        arrowcolor=COLORS["accent"],
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["bg_card"])],
        foreground=[("readonly", COLORS["text_primary"])],
        bordercolor=[("focus", COLORS["accent"])],
        lightcolor=[("focus", COLORS["accent"])],
        darkcolor=[("focus", COLORS["accent"])],
    )

    # ttk.Treeview
    style.configure(
        "Treeview",
        background=COLORS["bg_card"],
        fieldbackground=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        rowheight=28,
        bordercolor=COLORS["border"],
        font=fonts["body"],
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["accent"],
        foreground=COLORS["text_invert"],
        font=fonts["section"],
        relief="flat",
        padding=(10, 8),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", COLORS["accent_hover"])],
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["accent_soft"])],
        foreground=[("selected", COLORS["text_primary"])],
    )

    # ttk.Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["bg_main"],
        troughcolor=COLORS["bg_subtle"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["text_secondary"],
    )

    return fonts


# ------------------------------------------------------ WIDGET HELPERS ----
# These helpers style classic tk widgets (Button, Label, Frame, Toplevel, Entry)
# which don't honor ttk styles.

def _hover(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    def on_enter(_):
        widget.configure(bg=hover_bg)
        if hover_fg:
            widget.configure(fg=hover_fg)
    def on_leave(_):
        widget.configure(bg=normal_bg)
        if normal_fg:
            widget.configure(fg=normal_fg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def style_primary_button(btn, width=None):
    """Filled forest-green button — main calls to action."""
    btn.configure(
        bg=COLORS["accent"], fg=COLORS["text_invert"],
        activebackground=COLORS["accent_hover"],
        activeforeground=COLORS["text_invert"],
        relief="flat", borderwidth=0,
        font=fonts["button"],
        padx=18, pady=8,
        cursor="hand2",
        highlightthickness=0,
    )
    if width is not None:
        btn.configure(width=width)
    _hover(btn, COLORS["accent"], COLORS["accent_hover"])


def style_secondary_button(btn, width=None):
    """White / outlined button — secondary actions."""
    btn.configure(
        bg=COLORS["bg_card"], fg=COLORS["accent"],
        activebackground=COLORS["accent_soft"],
        activeforeground=COLORS["accent_hover"],
        relief="solid", borderwidth=1,
        font=fonts["button"],
        padx=16, pady=7,
        cursor="hand2",
        highlightthickness=0,
        highlightbackground=COLORS["border"],
    )
    if width is not None:
        btn.configure(width=width)
    _hover(btn, COLORS["bg_card"], COLORS["accent_soft"])


def style_ghost_button(btn, width=None):
    """Text-only button — Back / Close / Cancel."""
    btn.configure(
        bg=COLORS["bg_main"], fg=COLORS["text_secondary"],
        activebackground=COLORS["bg_subtle"],
        activeforeground=COLORS["text_primary"],
        relief="flat", borderwidth=0,
        font=fonts["button"],
        padx=14, pady=6,
        cursor="hand2",
        highlightthickness=0,
    )
    if width is not None:
        btn.configure(width=width)
    _hover(btn, COLORS["bg_main"], COLORS["bg_subtle"],
           normal_fg=COLORS["text_secondary"], hover_fg=COLORS["text_primary"])


def style_danger_button(btn, width=None):
    btn.configure(
        bg=COLORS["danger"], fg=COLORS["text_invert"],
        activebackground=COLORS["danger_hover"],
        activeforeground=COLORS["text_invert"],
        relief="flat", borderwidth=0,
        font=fonts["button"],
        padx=16, pady=7,
        cursor="hand2",
        highlightthickness=0,
    )
    if width is not None:
        btn.configure(width=width)
    _hover(btn, COLORS["danger"], COLORS["danger_hover"])


def style_label(lbl, kind="body", bg=None):
    """kind: title | subtitle | heading | section | body | body_bold | small | small_muted"""
    fg_map = {
        "title":       COLORS["text_primary"],
        "subtitle":    COLORS["text_secondary"],
        "heading":     COLORS["text_primary"],
        "section":     COLORS["accent"],
        "body":        COLORS["text_primary"],
        "body_bold":   COLORS["text_primary"],
        "small":       COLORS["text_secondary"],
        "small_muted": COLORS["text_muted"],
    }
    lbl.configure(
        font=fonts.get(kind, fonts["body"]),
        fg=fg_map.get(kind, COLORS["text_primary"]),
        bg=bg if bg is not None else COLORS["bg_main"],
    )


def style_entry(entry):
    entry.configure(
        bg=COLORS["bg_card"],
        fg=COLORS["text_primary"],
        relief="solid", borderwidth=1,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        insertbackground=COLORS["text_primary"],
        font=fonts["body"],
    )


def style_frame(frm, card=False):
    frm.configure(
        bg=COLORS["bg_card"] if card else COLORS["bg_main"],
        bd=0, highlightthickness=0,
    )


def style_toplevel(window, title=None):
    """Standard styling for popup windows (Toplevel)."""
    window.configure(bg=COLORS["bg_main"])
    if title is not None:
        window.title(title)


def hairline(parent, color=None, height=1, **pack_or_grid_kwargs):
    """Thin divider line. Caller handles geometry (.pack/.grid)."""
    from tkinter import Frame
    line = Frame(parent, bg=color or COLORS["divider"], height=height, bd=0)
    return line
