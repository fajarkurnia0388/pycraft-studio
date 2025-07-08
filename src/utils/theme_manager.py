"""
Tujuan: ThemeManager untuk mengelola tema (dark, light, custom) di PyCraft Studio
Dependensi: tkinter, ttk
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ThemeManager:
    """Mengelola tema aplikasi (default & custom) untuk PyCraft Studio."""
    DEFAULT_THEMES = {
        "light": {
            "background": "#f5f5f5",
            "foreground": "#222",
            "button_bg": "#e0e0e0",
            "button_fg": "#222",
            "accent": "#1976d2"
        },
        "dark": {
            "background": "#23272e",
            "foreground": "#f5f5f5",
            "button_bg": "#333a45",
            "button_fg": "#f5f5f5",
            "accent": "#90caf9"
        },
        "neon": {
            "background": "#181824",
            "foreground": "#39ff14",
            "button_bg": "#22223b",
            "button_fg": "#f72585",
            "accent": "#00f0ff"
        }
    }

    def __init__(self, root: tk.Tk, theme: str = "light", custom_themes: Optional[dict] = None, default_theme_overrides: Optional[dict] = None):
        self.root = root
        self.style = ttk.Style(self.root)
        self.theme = theme
        if custom_themes is None:
            self.custom_themes = {}
        else:
            self.custom_themes = custom_themes
        self.default_theme_overrides = default_theme_overrides or {}
        self.themes = dict(self.DEFAULT_THEMES)
        self.themes.update(self.custom_themes)
        self.apply_theme(self.theme)

    def get_available_themes(self):
        return list(self.themes.keys())

    def get_style_dict(self, theme: str):
        return self.themes.get(theme, self.DEFAULT_THEMES["light"])

    def apply_theme(self, theme: str):
        if theme not in self.themes:
            logger.warning(f"Tema tidak dikenal: {theme}, fallback ke light.")
            theme = "light"
        self.theme = theme
        style_dict = self.get_style_dict(theme)
        self._set_style(style_dict)
        self._force_refresh()

    def _set_style(self, style_dict):
        self.root.configure(bg=style_dict["background"])
        self.style.theme_use("clam")
        self.style.configure("TLabel", background=style_dict["background"], foreground=style_dict["foreground"])
        self.style.configure("TFrame", background=style_dict["background"])
        self.style.configure("TLabelframe", background=style_dict["background"], foreground=style_dict["foreground"])
        self.style.configure("TLabelframe.Label", background=style_dict["background"], foreground=style_dict["foreground"])
        self.style.configure("TButton", background=style_dict["button_bg"], foreground=style_dict["button_fg"], borderwidth=1)
        self.style.map("TButton",
            background=[("active", style_dict["accent"]), ("!active", style_dict["button_bg"])],
            foreground=[("active", style_dict["button_fg"]), ("!active", style_dict["button_fg"])],
        )
        self.style.configure("TEntry", fieldbackground=style_dict["background"], foreground=style_dict["foreground"])
        self.style.configure("TNotebook", background=style_dict["background"])
        self.style.configure("TNotebook.Tab", background=style_dict["button_bg"], foreground=style_dict["button_fg"])
        self.style.map("TNotebook.Tab",
            background=[("selected", style_dict["accent"]), ("!selected", style_dict["button_bg"])],
            foreground=[("selected", style_dict["button_fg"]), ("!selected", style_dict["button_fg"])],
        )
        self.style.configure("TCheckbutton", background=style_dict["background"], foreground=style_dict["foreground"])
        self.style.configure("TCombobox", fieldbackground=style_dict["background"], background=style_dict["background"], foreground=style_dict["foreground"])
        self.style.map("TCombobox",
            fieldbackground=[("readonly", style_dict["background"])],
            background=[("readonly", style_dict["background"])],
            foreground=[("readonly", style_dict["foreground"])]
        )

    def _force_refresh(self):
        try:
            self.root.update_idletasks()
            self.style.theme_use(self.style.theme_use())
        except Exception as e:
            logger.warning(f"Error saat force refresh style: {e}")

    def get_current_theme(self):
        return self.theme

    def set_theme_colors(self, theme: str, style_dict: dict):
        if theme in self.DEFAULT_THEMES:
            # Only update in-memory, not default
            self.themes[theme] = style_dict
        else:
            self.custom_themes[theme] = style_dict
            self.themes[theme] = style_dict
        if self.theme == theme:
            self.apply_theme(theme)

    def get_default_theme(self, theme: str):
        if theme in self.default_theme_overrides:
            return self.default_theme_overrides[theme]
        return self.DEFAULT_THEMES.get(theme, {})

    def reset_theme(self, theme: str):
        if theme in self.DEFAULT_THEMES:
            self.themes[theme] = dict(self.get_default_theme(theme))
            if self.theme == theme:
                self.apply_theme(theme)

    def set_default_theme(self, theme: str, style_dict: dict):
        self.default_theme_overrides[theme] = dict(style_dict)
        # Tidak langsung apply, hanya update default

    def add_custom_theme(self, name: str, style_dict: dict):
        if name in self.themes:
            raise ValueError("Theme name already exists")
        self.custom_themes[name] = style_dict
        self.themes[name] = style_dict

    def delete_custom_theme(self, name: str):
        if name in self.custom_themes:
            del self.custom_themes[name]
            del self.themes[name]
            if self.theme == name:
                self.apply_theme("light")

    def export_custom_themes(self):
        return self.custom_themes.copy() 