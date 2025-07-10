"""
Enhanced Main Window untuk PyCraft Studio.

GUI dengan fitur-fitur canggih untuk project management.
"""

import json
import logging
import os
import platform
import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, W, END, RIGHT, Y, DISABLED, NORMAL, LEFT, TOP, BOTTOM, E, N, S, WORD, X, SUNKEN
from tkinter import colorchooser, filedialog, messagebox, scrolledtext, StringVar, BooleanVar, IntVar
from typing import Any, Callable, Optional
from pathlib import Path
import urllib.request
import tkinter as tk

from ..core.config import ConfigManager
from ..core.enhanced_builder import EnhancedProjectBuilder
from ..utils.plugin_loader import get_available_plugins, load_plugins, unload_plugin
from ..utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class EnhancedMainWindow:
    """Enhanced main window dengan fitur project management."""

    def show_almanak(self, title, info_dict):
        win = tb.Toplevel(self.root)
        win.title(f"Info Detail {title}")
        win.geometry("800x420")
        win.transient(self.root)
        win.grab_set()
        frame = tb.Frame(win, padding=14)
        frame.pack(fill=BOTH, expand=True)
        header = tb.Label(
            frame, text=f"Info Detail {title}", font=("Arial", 15, "bold")
        )
        header.pack(anchor=W, pady=(0, 6))
        desc = tb.Label(
            frame,
            text="Perbandingan deskripsi, kelebihan, dan kekurangan setiap library.",
            foreground="gray",
            font=("Arial", 10),
        )
        desc.pack(anchor=W, pady=(0, 10))
        columns = ("Library", "Deskripsi", "Kelebihan", "Kekurangan")
        style = tb.Style()
        # Ambil style dari theme aktif
        style_dict = self.theme_manager.get_style_dict(self.theme_manager.get_current_theme())
        style.configure("Treeview",
            background=style_dict.get("background", "#fff"),
            foreground=style_dict.get("foreground", "#111"),
            fieldbackground=style_dict.get("background", "#fff"),
            font=("Arial", 10),
            borderwidth=1, relief="solid"
        )
        style.configure("Treeview.Heading",
            background=style_dict.get("button_bg", "#eee"),
            foreground=style_dict.get("button_fg", "#111"),
            font=("Arial", 11, "bold")
        )
        tree = tb.Treeview(frame, columns=columns, show="headings", height=8)
        for col, w in zip(columns, [110, 260, 200, 200]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=W, stretch=True)

        def wrap(text, width=40):
            import textwrap
            return "\n".join(textwrap.wrap(text, width=width))

        for idx, (lib, info) in enumerate(info_dict.items()):
            if lib == "None":
                continue
            deskripsi, plus, minus = (
                info["deskripsi"],
                info["kelebihan"],
                info["kekurangan"],
            )
            tree.insert(
                "",
                END,
                values=(lib, wrap(deskripsi, 40), wrap(plus, 28), wrap(minus, 28)),
                tags=("oddrow" if idx % 2 else "evenrow",),
            )
        # Zebra striping pakai warna dari theme
        tree.tag_configure("oddrow", background=style_dict.get("background", "#fff"))
        tree.tag_configure("evenrow", background=style_dict.get("button_bg", "#eee"))
        tree.pack(fill=BOTH, expand=True, pady=4, padx=2)
        # Scrollbar
        scrollbar = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 4))
        tb.Button(frame, text="Tutup", command=win.destroy).pack(pady=(12, 16))

    def show_gui_almanak(self):
        self.show_almanak("GUI Library", self.gui_info_dict)

    def show_backend_almanak(self):
        self.show_almanak("Backend", self.backend_info_dict)

    def show_database_almanak(self):
        self.show_almanak("Database", self.database_info_dict)

    def show_testing_almanak(self):
        self.show_almanak("Testing", self.testing_info_dict)

    def show_utility_almanak(self):
        self.show_almanak("Utility", self.utility_info_dict)

    def __init__(self) -> None:
        self.root = tb.Window(themename='darkly')
        self.root.title("PyCraft Studio - Enhanced")
        self.root.geometry("1000x700")

        # Initialize components
        self.config_manager = ConfigManager()
        self.builder = EnhancedProjectBuilder()

        # Initialize theme manager
        theme = self.config_manager.get_config("theme", "light")
        self.theme_manager = ThemeManager(self.root, theme=theme)

        # List widget yang perlu diubah warna manual
        self.themable_widgets = []

        # Status variables
        self.current_project_path = None
        self.build_thread = None
        self.wizard_button = None  # Untuk referensi tombol wizard
        self.build_in_progress = False

        # Muat plugin aktif
        active_plugins = self.config_manager.get_config("active_plugins", [])
        load_plugins(self, active_plugins)

        # Inisialisasi dict info (format baru: deskripsi, kelebihan, kekurangan)
        self.gui_info_dict = {
            "tkinter": {
                "deskripsi": "GUI bawaan Python, ringan, mudah dipelajari, cocok untuk aplikasi sederhana.",
                "kelebihan": "Built-in, ringan, mudah dipelajari",
                "kekurangan": "Tampilan klasik, fitur terbatas",
            },
            "PyQt": {
                "deskripsi": "Toolkit GUI modern berbasis Qt, banyak widget, tampilan profesional.",
                "kelebihan": "Fitur lengkap, tampilan modern",
                "kekurangan": "Lisensi GPL/commercial, size besar",
            },
            "wxPython": {
                "deskripsi": "Toolkit GUI cross-platform dengan tampilan native di tiap OS.",
                "kelebihan": "Native look, cross-platform",
                "kekurangan": "Dokumentasi kurang lengkap",
            },
            "PySide": {
                "deskripsi": "Alternatif PyQt dengan lisensi LGPL, API mirip Qt.",
                "kelebihan": "Mirip PyQt, LGPL",
                "kekurangan": "Komunitas lebih kecil dari PyQt",
            },
            "flet": {
                "deskripsi": "Framework GUI modern untuk web, desktop, dan mobile.",
                "kelebihan": "Web/desktop/mobile, modern",
                "kekurangan": "Masih baru, API berubah cepat",
            },
            "customtkinter": {
                "deskripsi": "Modernisasi Tkinter dengan dukungan dark mode dan widget modern.",
                "kelebihan": "Modernisasi Tkinter, dark mode",
                "kekurangan": "Bergantung pada Tkinter",
            },
            "None": {
                "deskripsi": "Tidak menggunakan library GUI.",
                "kelebihan": "-",
                "kekurangan": "-",
            },
        }
        self.backend_info_dict = {
            "Flask": {
                "deskripsi": "Framework web minimalis, cocok untuk REST API dan prototipe.",
                "kelebihan": "Minimalis, mudah dipelajari",
                "kekurangan": "Kurang cocok untuk skala besar",
            },
            "FastAPI": {
                "deskripsi": "Framework web modern, async, dokumentasi otomatis, performa tinggi.",
                "kelebihan": "Modern, async, dokumentasi otomatis",
                "kekurangan": "Masih muda, learning curve",
            },
            "Django": {
                "deskripsi": "Framework web fullstack, ORM, admin, cocok untuk aplikasi besar.",
                "kelebihan": "Lengkap, ORM, admin, mature",
                "kekurangan": "Berat untuk microservice",
            },
            "Tornado": {
                "deskripsi": "Framework web async, scalable, cocok untuk aplikasi real-time.",
                "kelebihan": "Async, scalable",
                "kekurangan": "API unik, komunitas kecil",
            },
            "Quart": {
                "deskripsi": "Framework web async, API mirip Flask, cocok untuk microservice async.",
                "kelebihan": "Flask async, mirip Flask",
                "kekurangan": "Komunitas kecil",
            },
            "Starlette": {
                "deskripsi": "Microframework async, basis FastAPI, ringan dan modular.",
                "kelebihan": "Micro, async, basis FastAPI",
                "kekurangan": "Fitur terbatas",
            },
            "None": {
                "deskripsi": "Tidak menggunakan backend.",
                "kelebihan": "-",
                "kekurangan": "-",
            },
        }
        self.database_info_dict = {
            "SQLite": {
                "deskripsi": "Database embedded, tanpa server, cocok untuk aplikasi kecil-menengah.",
                "kelebihan": "Embedded, tanpa server, mudah",
                "kekurangan": "Tidak cocok untuk skala besar",
            },
            "SQLAlchemy": {
                "deskripsi": "ORM powerful, mendukung banyak database relasional.",
                "kelebihan": "ORM powerful, multi-DB",
                "kekurangan": "Learning curve, verbose",
            },
            "MongoDB": {
                "deskripsi": "Database NoSQL dokumen, fleksibel, cocok untuk data tidak terstruktur.",
                "kelebihan": "NoSQL, fleksibel",
                "kekurangan": "Tidak relational, perlu driver",
            },
            "PostgreSQL": {
                "deskripsi": "Database relasional open source, fitur lengkap, cocok untuk aplikasi besar.",
                "kelebihan": "Fitur lengkap, open source",
                "kekurangan": "Setup lebih rumit dari SQLite",
            },
            "MySQL": {
                "deskripsi": "Database relasional populer, banyak resource dan dukungan.",
                "kelebihan": "Populer, banyak resource",
                "kekurangan": "Fitur lebih sedikit dari PostgreSQL",
            },
            "Peewee": {
                "deskripsi": "ORM ringan, mudah digunakan, cocok untuk aplikasi kecil.",
                "kelebihan": "ORM ringan, mudah",
                "kekurangan": "Fitur terbatas dibanding SQLAlchemy",
            },
            "TinyDB": {
                "deskripsi": "Database NoSQL embedded, mudah digunakan, cocok untuk prototipe.",
                "kelebihan": "NoSQL embedded, mudah",
                "kekurangan": "Tidak cocok untuk data besar",
            },
            "None": {
                "deskripsi": "Tidak menggunakan database.",
                "kelebihan": "-",
                "kekurangan": "-",
            },
        }
        self.testing_info_dict = {
            "pytest": {
                "deskripsi": "Framework testing modern, powerful, banyak plugin.",
                "kelebihan": "Modern, powerful, banyak plugin",
                "kekurangan": "Tidak built-in, learning curve",
            },
            "unittest": {
                "deskripsi": "Framework testing built-in Python, standar dan stabil.",
                "kelebihan": "Built-in, standar",
                "kekurangan": "Verbose, kurang modern",
            },
            "nose2": {
                "deskripsi": "Alternatif unittest, mendukung plugin dan discovery otomatis.",
                "kelebihan": "Alternatif unittest, plugin",
                "kekurangan": "Komunitas kecil",
            },
            "hypothesis": {
                "deskripsi": "Framework property-based testing, powerful untuk edge case.",
                "kelebihan": "Property-based, powerful",
                "kekurangan": "Learning curve, advanced",
            },
            "None": {
                "deskripsi": "Tidak menggunakan library testing.",
                "kelebihan": "-",
                "kekurangan": "-",
            },
        }
        self.utility_info_dict = {
            "click": {
                "deskripsi": "Library untuk membuat CLI dengan mudah dan rapi.",
                "kelebihan": "CLI builder, mudah",
                "kekurangan": "Fitur terbatas dibanding typer",
            },
            "typer": {
                "deskripsi": "Library CLI modern berbasis type hints, mirip click.",
                "kelebihan": "CLI modern, type hints",
                "kekurangan": "Masih muda, API berubah",
            },
            "rich": {
                "deskripsi": "Library untuk output terminal warna, tabel, progress bar, dsb.",
                "kelebihan": "Output terminal warna, tabel, dsb",
                "kekurangan": "Tidak untuk GUI",
            },
            "loguru": {
                "deskripsi": "Library logging modern, mudah digunakan, fitur lengkap.",
                "kelebihan": "Logging modern, mudah",
                "kekurangan": "Tidak built-in",
            },
            "colorama": {
                "deskripsi": "Library untuk warna terminal cross-platform.",
                "kelebihan": "Warna terminal cross-platform",
                "kekurangan": "Fitur terbatas",
            },
            "tqdm": {
                "deskripsi": "Progress bar CLI yang mudah dan fleksibel.",
                "kelebihan": "Progress bar CLI, mudah",
                "kekurangan": "Hanya progress bar",
            },
            "pydantic": {
                "deskripsi": "Validasi data dan parsing berbasis type hints, populer di FastAPI.",
                "kelebihan": "Validasi data, type hints",
                "kekurangan": "Learning curve, heavy untuk project kecil",
            },
            "None": {
                "deskripsi": "Tidak menggunakan library utility.",
                "kelebihan": "-",
                "kekurangan": "-",
            },
        }

        # Setup UI
        self.setup_ui()
        self.setup_menu()

        # Apply theme to all widgets after UI is complete
        self.root.after(
            100, self.update_widget_themes
        )  # Small delay to ensure widgets are rendered

        # Almanak pop-up functions
        # self.show_gui_almanak = lambda: show_almanak("GUI Library", self.gui_info_dict)
        # self.show_backend_almanak = lambda: show_almanak("Backend", self.backend_info_dict)
        # self.show_database_almanak = lambda: show_almanak("Database", self.database_info_dict)
        # self.show_testing_almanak = lambda: show_almanak("Testing", self.testing_info_dict)
        # self.show_utility_almanak = lambda: show_almanak("Utility", self.utility_info_dict)

        self.chemistry_comments = {
            # Desktop sederhana
            (
                "tkinter",
                "Flask",
                "SQLite",
                "pytest",
                "click",
            ): "Cocok untuk aplikasi desktop sederhana, deployment mudah, learning curve rendah.",
            (
                "tkinter",
                "None",
                "SQLite",
                "unittest",
                "None",
            ): "Aplikasi desktop lokal tanpa backend, cocok untuk tool internal atau prototipe.",
            (
                "customtkinter",
                "None",
                "SQLite",
                "unittest",
                "None",
            ): "Stack minimalis, cocok untuk prototipe offline.",
            (
                "wxPython",
                "None",
                "SQLite",
                "pytest",
                "None",
            ): "Aplikasi desktop native look, cocok untuk tool lintas OS.",
            # Desktop modern/enterprise
            (
                "PyQt",
                "FastAPI",
                "PostgreSQL",
                "pytest",
                "rich",
            ): "Stack modern untuk aplikasi desktop-enterprise, cocok untuk tim advanced.",
            (
                "PySide",
                "Starlette",
                "PostgreSQL",
                "pytest",
                "pydantic",
            ): "Stack async, cocok untuk aplikasi desktop dengan backend async dan validasi data ketat.",
            # Hybrid/web
            (
                "flet",
                "FastAPI",
                "MongoDB",
                "pytest",
                "typer",
            ): "Stack modern untuk aplikasi web/desktop hybrid, cocok untuk MVP dan rapid prototyping.",
            (
                "flet",
                "None",
                "TinyDB",
                "pytest",
                "tqdm",
            ): "Aplikasi desktop/web hybrid tanpa backend, database ringan, cocok untuk prototipe data kecil.",
            # Web API/CLI
            (
                "None",
                "Flask",
                "SQLite",
                "pytest",
                "click",
            ): "CLI/REST API sederhana tanpa GUI, cocok untuk microservice atau backend API.",
            (
                "None",
                "FastAPI",
                "MongoDB",
                "pytest",
                "typer",
            ): "Stack API modern, cocok untuk backend async dan validasi data dinamis.",
            (
                "None",
                "Django",
                "PostgreSQL",
                "pytest",
                "rich",
            ): "Stack web fullstack, cocok untuk aplikasi web skala besar.",
            # Kombinasi testing/utility
            (
                "tkinter",
                "Flask",
                "SQLite",
                "hypothesis",
                "loguru",
            ): "Stack desktop dengan REST API, cocok untuk pengujian property-based dan logging modern.",
            (
                "PyQt",
                "None",
                "MySQL",
                "nose2",
                "colorama",
            ): "Aplikasi desktop dengan database eksternal, testing dan output terminal warna.",
            # Kombinasi tanpa database
            (
                "tkinter",
                "Flask",
                "None",
                "pytest",
                "click",
            ): "Aplikasi desktop lokal, database embedded, testing dan CLI.",
            (
                "PyQt",
                "None",
                "SQLite",
                "pytest",
                "rich",
            ): "Aplikasi desktop modern, database embedded, output terminal kaya.",
            # Kombinasi minimal
            (
                "None",
                "None",
                "None",
                "None",
                "None",
            ): "Tidak ada stack terpilih. Silakan pilih minimal satu library.",
            # Kombinasi lain
            (
                "flet",
                "Flask",
                "SQLite",
                "pytest",
                "click",
            ): "Aplikasi hybrid dengan backend REST, database embedded, cocok untuk tool lintas platform.",
            (
                "customtkinter",
                "Flask",
                "SQLite",
                "pytest",
                "click",
            ): "Aplikasi desktop modern dengan backend REST, deployment mudah.",
            (
                "wxPython",
                "Django",
                "MySQL",
                "pytest",
                "loguru",
            ): "Cocok untuk aplikasi desktop dengan backend skala menengah, logging dan testing sudah terintegrasi.",
        }

        # Di __init__ atau setup_ui tambahkan:
        self.root.bind('<Control-n>', lambda e: self.notebook.select(1))  # Project Templates
        self.root.bind('<Control-b>', lambda e: self.notebook.select(2))  # Build
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        self.root.bind('<F1>', lambda e: self.show_about())

    def generate_chemistry_comment(self, libs_tuple):
        # libs_tuple: (gui, backend, database, testing, utility)
        gui, backend, database, testing, utility = libs_tuple
        parts = []
        # 2 kombinasi
        if (
            gui != "None"
            and backend != "None"
            and database == testing == utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan backend {backend}, cocok untuk client-server sederhana."
        if (
            gui != "None"
            and database != "None"
            and backend == testing == utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan database {database}, cocok untuk data lokal atau offline."
        if (
            backend != "None"
            and database != "None"
            and gui == testing == utility == "None"
        ):
            return f"Backend {backend} dengan database {database}, cocok untuk API/data service."
        if (
            backend != "None"
            and testing != "None"
            and gui == database == utility == "None"
        ):
            return f"Backend {backend} dengan testing {testing}, cocok untuk pengujian API."
        if (
            gui != "None"
            and testing != "None"
            and backend == database == utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan testing {testing}, cocok untuk pengujian aplikasi GUI."
        if (
            gui != "None"
            and utility != "None"
            and backend == database == testing == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan utility {utility}, menambah fitur CLI/logging/output."
        if (
            backend != "None"
            and utility != "None"
            and gui == database == testing == "None"
        ):
            return f"Backend {backend} dengan utility {utility}, cocok untuk API dengan CLI/logging."
        if (
            database != "None"
            and utility != "None"
            and gui == backend == testing == "None"
        ):
            return f"Database {database} dengan utility {utility}, cocok untuk tool data processing."
        # 3 kombinasi
        if (
            gui != "None"
            and backend != "None"
            and database != "None"
            and testing == utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan backend {backend} dan database {database}, cocok untuk client-server dengan data terpusat."
        if (
            gui != "None"
            and backend != "None"
            and testing != "None"
            and database == utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan backend {backend} dan testing {testing}, cocok untuk pengujian end-to-end."
        if (
            backend != "None"
            and database != "None"
            and testing != "None"
            and gui == utility == "None"
        ):
            return f"Backend {backend} dengan database {database} dan testing {testing}, cocok untuk API/data service teruji."
        if (
            backend != "None"
            and database != "None"
            and utility != "None"
            and gui == testing == "None"
        ):
            return f"Backend {backend} dengan database {database} dan utility {utility}, cocok untuk API dengan fitur CLI/logging."
        if (
            gui != "None"
            and database != "None"
            and utility != "None"
            and backend == testing == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan database {database} dan utility {utility}, cocok untuk tool data processing dengan output kaya."
        # 4 kombinasi
        if (
            gui != "None"
            and backend != "None"
            and database != "None"
            and testing != "None"
            and utility == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan backend {backend}, database {database}, dan testing {testing}, cocok untuk aplikasi client-server teruji."
        if (
            gui != "None"
            and backend != "None"
            and database != "None"
            and utility != "None"
            and testing == "None"
        ):
            return f"Aplikasi desktop ({gui}) dengan backend {backend}, database {database}, dan utility {utility}, cocok untuk aplikasi lengkap dengan fitur CLI/logging."
        if (
            backend != "None"
            and database != "None"
            and testing != "None"
            and utility != "None"
            and gui == "None"
        ):
            return f"Backend {backend} dengan database {database}, testing {testing}, dan utility {utility}, cocok untuk API/data service enterprise."
        # 5 kombinasi
        if all(x != "None" for x in libs_tuple):
            return f"Stack lengkap: aplikasi desktop ({gui}) dengan backend {backend}, database {database}, testing {testing}, dan utility {utility}. Cocok untuk aplikasi enterprise, maintainable, dan scalable."
        # 1 kombinasi
        if sum(x != "None" for x in libs_tuple) == 1:
            if gui != "None":
                return f"Aplikasi desktop ({gui}) tanpa backend/database."
            if backend != "None":
                return f"Backend {backend} tanpa database."
            if database != "None":
                return f"Database {database} standalone."
            if testing != "None":
                return f"Testing {testing} standalone."
            if utility != "None":
                return f"Utility {utility} standalone."
        # Kombinasi lain
        return "Belum ada analisis kemistri untuk kombinasi ini."

    def update_chemistry_comment(self):
        gui = self.gui_library_var.get()
        backend = self.backend_var.get()
        database = self.database_var.get()
        testing = self.testing_var.get()
        utility = self.utility_var.get()
        key = (gui, backend, database, testing, utility)
        if key in self.chemistry_comments:
            comment = self.chemistry_comments[key]
        else:
            comment = self.generate_chemistry_comment(key)
        self.template_info_text.insert(END, f"\n\n[Analisis Kemistri]\n{comment}\n")

    def setup_ui(self) -> None:
        """Setup user interface."""
        # Create notebook for tabs
        self.notebook = tb.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_dashboard_tab()  # Tambahkan tab dashboard di awal
        self.create_build_tab()
        self.create_project_tab()
        self.create_analysis_tab()
        self.create_validation_tab()
        self.create_settings_tab()

        # Status bar
        self.status_bar = tb.Label(self.root, text="Ready", relief=SUNKEN)
        self.status_bar.pack(side=BOTTOM, fill=X)
        # Tambahkan status bar ke themable_widgets
        self.themable_widgets.append(self.status_bar)

    def create_dashboard_tab(self) -> None:
        """Create dashboard tab untuk statistik build, health check, dan history."""
        dashboard_frame = tb.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")

        # Statistik Build
        stats_frame = tb.LabelFrame(
            dashboard_frame, text="Statistik Build", padding=10
        )
        stats_frame.pack(fill=X, padx=10, pady=5)
        tb.Label(stats_frame, text="Total Build: 0").grid(row=0, column=0, sticky=W)
        tb.Label(stats_frame, text="Build Berhasil: 0").grid(
            row=1, column=0, sticky=W
        )
        tb.Label(stats_frame, text="Build Gagal: 0").grid(row=2, column=0, sticky=W)

        # Health Check
        health_frame = tb.LabelFrame(dashboard_frame, text="Health Check", padding=10)
        health_frame.pack(fill=X, padx=10, pady=5)
        tb.Label(health_frame, text="Status: OK").pack(anchor=W)
        tb.Label(health_frame, text="Resource Usage: CPU 0%, RAM 0MB").pack(
            anchor=W
        )

        # History
        history_frame = tb.LabelFrame(
            dashboard_frame, text="History Build", padding=10
        )
        history_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.history_text = scrolledtext.ScrolledText(history_frame, height=8)
        self.history_text.pack(fill=BOTH, expand=True)
        self.themable_widgets.append(self.history_text)

    def create_build_tab(self) -> None:
        """Create build tab."""
        build_frame = tb.Frame(self.notebook)
        self.notebook.add(build_frame, text="Build")

        # Deteksi OS user
        os_name = platform.system()
        if os_name == "Linux":
            default_format = "binary"
        elif os_name == "Windows":
            default_format = "exe"
        elif os_name == "Darwin":
            default_format = "app"
        else:
            default_format = "binary"

        # File selection
        file_frame = tb.LabelFrame(build_frame, text="File Selection", padding=10)
        file_frame.pack(fill=X, padx=10, pady=5)

        tb.Label(file_frame, text="Python File:").grid(row=0, column=0, sticky=W)
        self.file_path_var = StringVar()
        tb.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(
            row=0, column=1, padx=5
        )
        btn_browse_file = tb.Button(file_frame, text="📁", command=self.browse_file, width=2)
        btn_browse_file.grid(row=0, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_file, "Pilih folder/file")
        btn_file_help = tb.Button(file_frame, text="?", width=2, command=lambda: self.show_field_help("file_path"))
        btn_file_help.grid(row=0, column=3, sticky=W, padx=2)
        ToolTip(btn_file_help, "Bantuan/penjelasan")

        # Build options
        options_frame = tb.LabelFrame(build_frame, text="Build Options", padding=10)
        options_frame.pack(fill=X, padx=10, pady=5)

        # Output Format
        tb.Label(options_frame, text="Output Format:").grid(
            row=0, column=0, sticky=W
        )
        self.format_var = StringVar(value=default_format)
        format_combo = tb.Combobox(
            options_frame,
            textvariable=self.format_var,
            values=["exe", "app", "binary"],
            state="readonly",
            width=10,
        )
        format_combo.grid(row=0, column=1, padx=5, sticky=W)
        btn_format_info = tb.Button(options_frame, text="i", width=2, command=self.show_multiplatform_almanak)
        btn_format_info.grid(row=0, column=2, sticky=W, padx=2)
        ToolTip(btn_format_info, "Lihat info detail")
        tb.Button(
            options_frame,
            text="?",
            width=2,
            command=lambda: self.show_build_help("format"),
        ).grid(row=0, column=3, sticky=W, padx=2)
        ToolTip(tb.Button(options_frame, text="?", width=2), "Bantuan/penjelasan")

        # Info label di bawah selector
        self.format_info_var = StringVar()
        info_label = tb.Label(
            options_frame,
            textvariable=self.format_info_var,
            font=("Arial", 9, "italic"),
        )
        info_label.grid(row=1, column=1, columnspan=3, sticky=W, pady=(0, 4))

        # Terapkan warna kontras dengan background theme
        if hasattr(self, "theme_manager"):
            theme = self.theme_manager.get_current_theme()
            style_dict = self.theme_manager.get_style_dict(theme)
            bg = style_dict.get("background", "#fff")

            # Fungsi sederhana deteksi terang/gelap
            def is_dark(color):
                color = color.lstrip("#")
                r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
                return (r * 0.299 + g * 0.587 + b * 0.114) < 186

            fg = "#fff" if is_dark(bg) else "#111"
            try:
                info_label.configure(foreground=fg)
            except Exception:
                pass

        def update_format_info(*args):
            fmt = self.format_var.get()
            if (
                (os_name == "Linux" and fmt == "binary")
                or (os_name == "Windows" and fmt == "exe")
                or (os_name == "Darwin" and fmt == "app")
            ):
                self.format_info_var.set("Build akan dilakukan secara lokal di OS ini.")
                self.build_button.config(state=NORMAL)
            else:
                self.format_info_var.set(
                    f"Build format '{fmt}' hanya bisa dilakukan via GitHub Actions (multiplatform). Silakan push tag ke repo untuk build otomatis."
                )
                self.build_button.config(state=DISABLED)

        self.format_var.trace_add("write", update_format_info)

        # Build Mode
        tb.Label(options_frame, text="Build Mode:").grid(row=2, column=0, sticky=W)
        self.build_mode_var = StringVar(value="Release")
        mode_combo = tb.Combobox(
            options_frame,
            textvariable=self.build_mode_var,
            values=["Release", "Debug"],
            state="readonly",
        )
        mode_combo.grid(row=2, column=1, padx=5, sticky=W)
        tb.Button(
            options_frame,
            text="?",
            width=2,
            command=lambda: self.show_build_help("mode"),
        ).grid(row=2, column=2, sticky=W, padx=2)
        ToolTip(tb.Button(options_frame, text="?", width=2), "Bantuan/penjelasan")

        # Onefile/Onedir
        tb.Label(options_frame, text="Bundle Mode:").grid(row=3, column=0, sticky=W)
        self.bundle_mode_var = StringVar(value="onefile")
        bundle_combo = tb.Combobox(
            options_frame,
            textvariable=self.bundle_mode_var,
            values=["onefile", "onedir"],
            state="readonly",
        )
        bundle_combo.grid(row=3, column=1, padx=5, sticky=W)
        tb.Button(
            options_frame,
            text="?",
            width=2,
            command=lambda: self.show_build_help("bundle"),
        ).grid(row=3, column=2, sticky=W, padx=2)
        ToolTip(tb.Button(options_frame, text="?", width=2), "Bantuan/penjelasan")

        # Preset
        tb.Label(options_frame, text="Preset:").grid(row=4, column=0, sticky=W)
        self.preset_var = StringVar(value="Fast")
        preset_combo = tb.Combobox(
            options_frame,
            textvariable=self.preset_var,
            values=["Fast", "Minimal", "Debug"],
            state="readonly",
        )
        preset_combo.grid(row=4, column=1, padx=5, sticky=W)
        tb.Button(
            options_frame,
            text="?",
            width=2,
            command=lambda: self.show_build_help("preset"),
        ).grid(row=4, column=2, sticky=W, padx=2)
        ToolTip(tb.Button(options_frame, text="?", width=2), "Bantuan/penjelasan")

        # Output Directory
        tb.Label(options_frame, text="Output Directory:").grid(
            row=5, column=0, sticky=W
        )
        self.output_dir_var = StringVar(value="output")
        tb.Entry(options_frame, textvariable=self.output_dir_var, width=40).grid(
            row=5, column=1, padx=5, sticky=W
        )
        btn_browse_output = tb.Button(options_frame, text="📁", command=self.browse_output_dir, width=2)
        btn_browse_output.grid(row=5, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_output, "Pilih folder/file")
        btn_output_help = tb.Button(options_frame, text="?", width=2, command=lambda: self.show_field_help("output_dir"))
        btn_output_help.grid(row=5, column=3, sticky=W, padx=2)
        ToolTip(btn_output_help, "Bantuan/penjelasan")

        # Custom build arguments
        tb.Label(options_frame, text="Custom Build Args:").grid(
            row=6, column=0, sticky=W
        )
        self.custom_args_var = StringVar()
        tb.Entry(options_frame, textvariable=self.custom_args_var, width=40).grid(
            row=6, column=1, padx=5, sticky=W
        )
        tb.Button(
            options_frame, text="i", width=2, command=self.show_custom_args_almanak
        ).grid(row=6, column=2, sticky=W, padx=2)
        tb.Button(
            options_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("custom_args"),
        ).grid(row=6, column=3, sticky=W, padx=2)
        ToolTip(tb.Button(options_frame, text="i", width=2), "Lihat info detail")
        ToolTip(tb.Button(options_frame, text="?", width=2), "Bantuan/penjelasan")

        # Preview command line
        self.preview_cmd_var = StringVar(value="")
        tb.Label(options_frame, text="Preview Command:").grid(
            row=7, column=0, sticky=W
        )
        preview_entry = tb.Entry(
            options_frame, textvariable=self.preview_cmd_var, width=70, state="readonly"
        )
        preview_entry.grid(row=7, column=1, columnspan=3, padx=5, sticky=W)

        # Terapkan warna foreground sesuai theme
        if hasattr(self, "theme_manager"):
            theme = self.theme_manager.get_current_theme()
            style_dict = self.theme_manager.get_style_dict(theme)
            fg_color = style_dict.get("foreground")
            if fg_color:
                try:
                    preview_entry.configure(foreground=fg_color)
                except Exception:
                    pass
        self.themable_widgets.append(preview_entry)

        # Update preview command setiap opsi berubah
        for var in [
            self.format_var,
            self.build_mode_var,
            self.bundle_mode_var,
            self.preset_var,
            self.output_dir_var,
            self.custom_args_var,
            self.file_path_var,
        ]:
            var.trace_add("write", lambda *args: self.update_preview_command())

        # Build buttons
        button_frame = tb.Frame(build_frame)
        button_frame.pack(fill=X, padx=10, pady=5)

        self.build_button = tb.Button(
            button_frame, text="Build", command=self.start_build
        )
        self.build_button.pack(side=LEFT, padx=5)

        self.cancel_button = tb.Button(
            button_frame, text="Cancel", command=self.cancel_build, state=DISABLED
        )
        self.cancel_button.pack(side=LEFT, padx=5)

        # Progress
        progress_frame = tb.LabelFrame(build_frame, text="Progress", padding=10)
        progress_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.progress_var = StringVar(value="Ready")
        tb.Label(progress_frame, textvariable=self.progress_var).pack(anchor=W)

        self.progress_bar = tb.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill=X, pady=5)

        # Log output
        log_frame = tb.LabelFrame(build_frame, text="Build Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=BOTH, expand=True)
        # Tambahkan log_text ke themable_widgets
        self.themable_widgets.append(self.log_text)

        # Inisialisasi info format dan state tombol build
        update_format_info()

    def show_build_help(self, key):
        help_texts = {
            "format": (
                "Output Format:\n"
                "- exe: Build untuk Windows (.exe), bisa dijalankan di OS Windows.\n"
                "- app: Build untuk macOS (.app), bisa dijalankan di Mac.\n"
                "- binary: Build untuk Linux (file executable), bisa dijalankan di Linux.\n"
                "\nPilih sesuai target OS aplikasi Anda."
            ),
            "mode": (
                "Build Mode:\n"
                "- Release: Build optimal untuk distribusi ke user, ukuran lebih kecil, tanpa debug symbol.\n"
                "- Debug: Build untuk keperluan debugging, menyertakan symbol/log detail, ukuran lebih besar.\n"
                "\nGunakan Debug saat pengembangan, Release untuk rilis ke user."
            ),
            "bundle": (
                "Bundle Mode:\n"
                "- onefile: Semua file aplikasi dibundle menjadi satu file executable.\n"
                "- onedir: Hasil build berupa satu folder berisi executable dan dependensi.\n"
                "\nOnefile lebih praktis untuk distribusi, onedir lebih mudah untuk debugging."
            ),
            "preset": (
                "Preset Build:\n"
                "- Fast: Build cepat, pengaturan default, cocok untuk development/testing.\n"
                "- Minimal: Build dengan ukuran file sekecil mungkin (strip symbol, tanpa UPX).\n"
                "- Debug: Build dengan log detail dan debug symbol, cocok untuk troubleshooting.\n"
                "\nPilih preset sesuai kebutuhan build Anda."
            ),
            "output": (
                "Output Directory:\n"
                "Folder tujuan hasil build. Semua file hasil build akan disimpan di sini.\n"
                "Pastikan folder writable dan punya cukup ruang."
            ),
            "args": (
                "Custom Build Args:\n"
                "Argumen tambahan untuk builder, misal:\n"
                "  --icon=myicon.ico   (set icon aplikasi)\n"
                "  --hidden-import=x   (tambahkan modul tersembunyi)\n"
                "  --add-data=src:dst (copy data ke hasil build)\n"
                "\nLihat dokumentasi builder (misal: PyInstaller) untuk opsi lengkap."
            ),
        }
        msg = help_texts.get(key, "Tidak ada info.")
        messagebox.showinfo("Info Build Option", msg, parent=self.root)

    def update_preview_command(self):
        # Generate preview command line dari opsi build
        file = self.file_path_var.get() or "main.py"
        fmt = self.format_var.get()
        outdir = self.output_dir_var.get() or "output"
        custom = self.custom_args_var.get()
        # Gunakan builder untuk generate argumen build final
        if hasattr(self, "builder") and hasattr(self.builder, "get_final_build_args"):
            project_dir = str(Path(file).parent)
            final_args = self.builder.get_final_build_args(project_dir, fmt, custom)
            cmd = ["pyinstaller"] + final_args + [file, f"--distpath={outdir}"]
            self.preview_cmd_var.set(" ".join(cmd))
        else:
            # Fallback lama
            cmd = f"pyinstaller {file} --distpath {outdir}"
            if fmt == "exe":
                cmd += " --windowed"
            if custom:
                cmd += f" {custom}"
            self.preview_cmd_var.set(cmd)

    def create_project_tab(self) -> None:
        """Create project template tab."""
        project_frame = tb.Frame(self.notebook)
        self.notebook.add(project_frame, text="Project Templates")

        # Template selection
        template_frame = tb.LabelFrame(
            project_frame, text="Create New Project", padding=10
        )
        template_frame.pack(fill=X, padx=10, pady=5)

        tb.Label(template_frame, text="Project Name:").grid(
            row=0, column=0, sticky=W
        )
        self.project_name_var = StringVar()
        self.entry_project_name = tb.Entry(template_frame, textvariable=self.project_name_var, width=30)
        self.entry_project_name.grid(row=0, column=1, padx=5, sticky=W)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("project_name"),
        ).grid(row=0, column=2, sticky=W, padx=2)
        btn_template_help = tb.Button(template_frame, text="?", width=2, command=lambda: self.show_field_help("template"))
        btn_template_help.grid(row=1, column=2, sticky=W, padx=2)
        ToolTip(btn_template_help, "Bantuan/penjelasan")

        tb.Label(template_frame, text="Template:").grid(row=1, column=0, sticky=W)
        self.template_var = StringVar()
        templates = self.builder.get_available_templates()
        template_combo = tb.Combobox(
            template_frame,
            textvariable=self.template_var,
            values=templates,
            state="readonly",
        )
        template_combo.grid(row=1, column=1, padx=5, sticky=W)
        template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("template"),
        ).grid(row=1, column=2, sticky=W, padx=2)

        tb.Label(template_frame, text="Output Path:").grid(
            row=2, column=0, sticky=W
        )
        self.project_path_var = StringVar()
        self.entry_project_path = tb.Entry(template_frame, textvariable=self.project_path_var, width=50)
        self.entry_project_path.grid(row=2, column=1, padx=5, sticky=W)
        btn_browse_project = tb.Button(template_frame, text="📁", command=self.browse_project_output, width=2)
        btn_browse_project.grid(row=2, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_project, "Pilih folder/file")
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("output_path"),
        ).grid(row=2, column=3, sticky=W, padx=2)
        ToolTip(tb.Button(template_frame, text="?", width=2), "Bantuan/penjelasan")

        # GUI Library Selector
        tb.Label(template_frame, text="GUI Library:").grid(
            row=3, column=0, sticky=W
        )
        self.gui_library_var = StringVar()
        gui_libraries = [
            "tkinter",
            "PyQt",
            "wxPython",
            "PySide",
            "flet",
            "customtkinter",
            "None",
        ]
        gui_combo = tb.Combobox(
            template_frame,
            textvariable=self.gui_library_var,
            values=gui_libraries,
            state="readonly",
        )
        gui_combo.grid(row=3, column=1, padx=5, sticky=W)
        gui_combo.set(gui_libraries[0])
        btn_gui_info = tb.Button(template_frame, text="i", width=2, command=self.show_gui_almanak)
        btn_gui_info.grid(row=3, column=2, sticky=W, padx=2)
        ToolTip(btn_gui_info, "Lihat info detail")
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("gui_library"),
        ).grid(row=3, column=3, sticky=W, padx=2)
        ToolTip(tb.Button(template_frame, text="?", width=2), "Bantuan/penjelasan")

        # Backend Selector (opsional, lengkap)
        tb.Label(template_frame, text="Backend (opsional):").grid(
            row=4, column=0, sticky=W
        )
        self.backend_var = StringVar()
        backend_libs = [
            "None",
            "Flask",
            "FastAPI",
            "Django",
            "Tornado",
            "Quart",
            "Starlette",
        ]
        backend_combo = tb.Combobox(
            template_frame,
            textvariable=self.backend_var,
            values=backend_libs,
            state="readonly",
        )
        backend_combo.grid(row=4, column=1, padx=5, sticky=W)
        backend_combo.set(backend_libs[0])
        backend_info_btn = tb.Button(
            template_frame, text="i", width=2, command=self.show_backend_almanak
        )
        backend_info_btn.grid(row=4, column=2, sticky=W, padx=2)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("backend"),
        ).grid(row=4, column=3, sticky=W, padx=2)

        # Database Selector (opsional, lengkap)
        tb.Label(template_frame, text="Database (opsional):").grid(
            row=5, column=0, sticky=W
        )
        self.database_var = StringVar()
        database_libs = [
            "None",
            "SQLite",
            "SQLAlchemy",
            "MongoDB",
            "PostgreSQL",
            "MySQL",
            "Peewee",
            "TinyDB",
        ]
        database_combo = tb.Combobox(
            template_frame,
            textvariable=self.database_var,
            values=database_libs,
            state="readonly",
        )
        database_combo.grid(row=5, column=1, padx=5, sticky=W)
        database_combo.set(database_libs[0])
        database_info_btn = tb.Button(
            template_frame, text="i", width=2, command=self.show_database_almanak
        )
        database_info_btn.grid(row=5, column=2, sticky=W, padx=2)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("database"),
        ).grid(row=5, column=3, sticky=W, padx=2)

        # Testing Selector (opsional, lengkap)
        tb.Label(template_frame, text="Testing (opsional):").grid(
            row=6, column=0, sticky=W
        )
        self.testing_var = StringVar()
        testing_libs = ["None", "pytest", "unittest", "nose2", "hypothesis"]
        testing_combo = tb.Combobox(
            template_frame,
            textvariable=self.testing_var,
            values=testing_libs,
            state="readonly",
        )
        testing_combo.grid(row=6, column=1, padx=5, sticky=W)
        testing_combo.set(testing_libs[0])
        testing_info_btn = tb.Button(
            template_frame, text="i", width=2, command=self.show_testing_almanak
        )
        testing_info_btn.grid(row=6, column=2, sticky=W, padx=2)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("testing"),
        ).grid(row=6, column=3, sticky=W, padx=2)

        # Utility Selector (opsional, lengkap)
        tb.Label(template_frame, text="Utility (opsional):").grid(
            row=7, column=0, sticky=W
        )
        self.utility_var = StringVar()
        utility_libs = [
            "None",
            "click",
            "typer",
            "rich",
            "loguru",
            "colorama",
            "tqdm",
            "pydantic",
        ]
        utility_combo = tb.Combobox(
            template_frame,
            textvariable=self.utility_var,
            values=utility_libs,
            state="readonly",
        )
        utility_combo.grid(row=7, column=1, padx=5, sticky=W)
        utility_combo.set(utility_libs[0])
        utility_info_btn = tb.Button(
            template_frame, text="i", width=2, command=self.show_utility_almanak
        )
        utility_info_btn.grid(row=7, column=2, sticky=W, padx=2)
        tb.Button(
            template_frame,
            text="?",
            width=2,
            command=lambda: self.show_field_help("utility"),
        ).grid(row=7, column=3, sticky=W, padx=2)

        # Custom Project Rules & Background
        self.custom_projectrules = ''
        self.custom_background = ''
        def open_custom_projectrules():
            win = tb.Toplevel(self.root)
            win.title("Custom Project Rules")
            win.geometry("600x400")
            txt = tb.Text(win, wrap=WORD)
            txt.pack(fill=BOTH, expand=True, padx=10, pady=10)
            txt.insert(1.0, self.custom_projectrules or "# Aturan Coding & Best Practice\n...")
            def save_and_close():
                self.custom_projectrules = txt.get(1.0, END).strip()
                win.destroy()
            tb.Button(win, text="Simpan", command=save_and_close).pack(pady=5)
        def open_custom_background():
            win = tb.Toplevel(self.root)
            win.title("Custom Background")
            win.geometry("600x400")
            txt = tb.Text(win, wrap=WORD)
            txt.pack(fill=BOTH, expand=True, padx=10, pady=10)
            txt.insert(1.0, self.custom_background or "# Latar Belakang & Tujuan Project\n...")
            def save_and_close():
                self.custom_background = txt.get(1.0, END).strip()
                win.destroy()
            tb.Button(win, text="Simpan", command=save_and_close).pack(pady=5)
        btn_custom_rules = tb.Button(template_frame, text="Custom Project Rules", command=open_custom_projectrules)
        btn_custom_rules.grid(row=8, column=0, pady=8, sticky=W)
        ToolTip(btn_custom_rules, "Atur aturan coding")
        btn_custom_bg = tb.Button(template_frame, text="Custom Background", command=open_custom_background)
        btn_custom_bg.grid(row=8, column=1, pady=8, sticky=W)
        ToolTip(btn_custom_bg, "Atur latar belakang project")
        # HAPUS btn_lib_guide di sini!

        # Setelah tombol Custom Project Rules & Custom Background
        def show_lib_guide():
            win = tb.Toplevel(self.root)
            win.title("Panduan Kombinasi Library")
            win.geometry("900x500")
            frame = tb.Frame(win, padding=14)
            frame.pack(fill=BOTH, expand=True)
            header = tb.Label(frame, text="Panduan Kombinasi Library Populer", font=("Arial", 15, "bold"))
            header.pack(anchor=W, pady=(0, 6))
            desc = tb.Label(frame, text="Analisis kombinasi stack (GUI, Backend, Database, Testing, Utility) beserta kelebihan/kekurangan.", foreground="gray", font=("Arial", 10))
            desc.pack(anchor=W, pady=(0, 10))
            columns = ("GUI", "Backend", "Database", "Testing", "Utility", "Analisis")
            style = tb.Style()
            style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
            style.configure("Treeview", rowheight=38, font=("Arial", 10), borderwidth=1, relief="solid")
            tree = tb.Treeview(frame, columns=columns, show="headings", height=10)
            for col, w in zip(columns, [90, 110, 110, 90, 90, 350]):
                tree.heading(col, text=col)
                tree.column(col, width=w, anchor=W, stretch=True)
            # Isi data dari chemistry_comments
            for key, comment in self.chemistry_comments.items():
                gui, backend, db, test, util = key
                tree.insert("", END, values=(gui, backend, db, test, util, comment))
            # Tambahkan beberapa kombinasi dinamis (generate_chemistry_comment)
            sample_keys = [
                ("tkinter", "None", "SQLite", "pytest", "click"),
                ("PyQt", "Flask", "PostgreSQL", "pytest", "rich"),
                ("customtkinter", "FastAPI", "MongoDB", "unittest", "loguru"),
                ("flet", "None", "None", "pytest", "typer"),
            ]
            for key in sample_keys:
                if key not in self.chemistry_comments:
                    comment = self.generate_chemistry_comment(key)
                    gui, backend, db, test, util = key
                    tree.insert("", END, values=(gui, backend, db, test, util, comment))
            tree.pack(fill=BOTH, expand=True)
            # Scrollbar
            vsb = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree['yscrollcommand'] = vsb.set
            vsb.pack(side=RIGHT, fill=Y)
        # BUAT btn_lib_guide SETELAH show_lib_guide
        btn_lib_guide = tb.Button(template_frame, text="!?", command=show_lib_guide, width=2)
        btn_lib_guide.grid(row=8, column=2, pady=8, sticky=W)
        ToolTip(btn_lib_guide, "Panduan kombinasi library")

        # Template info
        info_frame = tb.LabelFrame(
            project_frame, text="Template Information", padding=10
        )
        info_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.template_info_text = scrolledtext.ScrolledText(info_frame, height=8)
        self.template_info_text.pack(fill=BOTH, expand=True)
        self.themable_widgets.append(self.template_info_text)

        # Create button
        button_frame = tb.Frame(project_frame)
        button_frame.pack(fill=X, padx=10, pady=5)

        self.create_project_button = tb.Button(
            button_frame, text="Create Project", command=self.create_project
        )
        self.create_project_button.pack(side=LEFT, padx=5)

        # Wizard Project Baru hanya jika fitur beta aktif
        if self.config_manager.get_config(
            "enable_beta_features", False
        ) and self.config_manager.get_config("enable_project_wizard_beta", False):
            self.wizard_button = tb.Button(
                button_frame,
                text="Wizard Project Baru (Beta)",
                command=self.open_project_wizard,
            )
            self.wizard_button.pack(side=LEFT, padx=5)

        for var in [
            self.gui_library_var,
            self.backend_var,
            self.database_var,
            self.testing_var,
            self.utility_var,
        ]:
            var.trace_add("write", lambda *args: self.show_template_and_chemistry())

    def create_analysis_tab(self) -> None:
        """Create dependency analysis tab."""
        analysis_frame = tb.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Dependency Analysis")

        # Project selection
        project_frame = tb.LabelFrame(
            analysis_frame, text="Project Analysis", padding=10
        )
        project_frame.pack(fill=X, padx=10, pady=5)

        tb.Label(project_frame, text="Project Path:").grid(
            row=0, column=0, sticky=W
        )
        self.analysis_path_var = StringVar()
        tb.Entry(project_frame, textvariable=self.analysis_path_var, width=50).grid(
            row=0, column=1, padx=5, sticky=W
        )
        btn_browse_analysis = tb.Button(project_frame, text="📁", command=self.browse_analysis_path, width=2)
        btn_browse_analysis.grid(row=0, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_analysis, "Pilih folder/file")

        btn_analysis_help = tb.Button(project_frame, text="?", width=2, command=lambda: self.show_field_help("analysis_path"))
        btn_analysis_help.grid(row=0, column=3, sticky=W, padx=2)
        ToolTip(btn_analysis_help, "Bantuan/penjelasan")

        # Analysis buttons
        button_frame = tb.Frame(analysis_frame)
        button_frame.pack(fill=X, padx=10, pady=5)

        tb.Button(
            button_frame, text="Analyze Project", command=self.analyze_project
        ).pack(side=LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Generate Requirements",
            command=self.generate_requirements,
        ).pack(side=LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Validate Dependencies",
            command=self.validate_dependencies,
        ).pack(side=LEFT, padx=5)

        # Analysis results
        results_frame = tb.LabelFrame(
            analysis_frame, text="Analysis Results", padding=10
        )
        results_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.analysis_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.analysis_text.pack(fill=BOTH, expand=True)
        self.themable_widgets.append(self.analysis_text)

    def create_validation_tab(self) -> None:
        """Create project validation tab."""
        validation_frame = tb.Frame(self.notebook)
        self.notebook.add(validation_frame, text="Project Validation")

        # Project selection
        project_frame = tb.LabelFrame(
            validation_frame, text="Project Validation", padding=10
        )
        project_frame.pack(fill=X, padx=10, pady=5)

        tb.Label(project_frame, text="Project Path:").grid(
            row=0, column=0, sticky=W
        )
        self.validation_path_var = StringVar()
        tb.Entry(project_frame, textvariable=self.validation_path_var, width=50).grid(
            row=0, column=1, padx=5, sticky=W
        )
        btn_browse_validation = tb.Button(project_frame, text="📁", command=self.browse_validation_path, width=2)
        btn_browse_validation.grid(row=0, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_validation, "Pilih folder/file")

        btn_validation_help = tb.Button(project_frame, text="?", width=2, command=lambda: self.show_field_help("validation_path"))
        btn_validation_help.grid(row=0, column=3, sticky=W, padx=2)
        ToolTip(btn_validation_help, "Bantuan/penjelasan")

        # Validation buttons
        button_frame = tb.Frame(validation_frame)
        button_frame.pack(fill=X, padx=10, pady=5)

        tb.Button(
            button_frame, text="Validate Structure", command=self.validate_structure
        ).pack(side=LEFT, padx=5)
        tb.Button(
            button_frame, text="Generate Report", command=self.generate_report
        ).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Fix Structure", command=self.fix_structure).pack(
            side=LEFT, padx=5
        )

        # Validation results
        results_frame = tb.LabelFrame(
            validation_frame, text="Validation Results", padding=10
        )
        results_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.validation_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.validation_text.pack(fill=BOTH, expand=True)
        self.themable_widgets.append(self.validation_text)

    def create_settings_tab(self) -> None:
        """Create settings tab."""
        settings_frame = tb.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")

        # Settings
        config_frame = tb.LabelFrame(settings_frame, text="Configuration", padding=10)
        config_frame.pack(fill=X, padx=10, pady=5)

        # Default output directory
        tb.Label(config_frame, text="Default Output Directory:").grid(
            row=0, column=0, sticky=W
        )
        self.default_output_var = StringVar(
            value=self.config_manager.get_config("default_output_dir", "output")
        )
        tb.Entry(config_frame, textvariable=self.default_output_var, width=40).grid(
            row=0, column=1, padx=5, sticky=W
        )
        btn_browse_default_output = tb.Button(config_frame, text="📁", command=self.browse_default_output, width=2)
        btn_browse_default_output.grid(row=0, column=2, sticky=W, padx=2)
        ToolTip(btn_browse_default_output, "Pilih folder/file")

        btn_default_output_help = tb.Button(config_frame, text="?", width=2, command=lambda: self.show_field_help("default_output"))
        btn_default_output_help.grid(row=0, column=3, sticky=W, padx=2)
        ToolTip(btn_default_output_help, "Bantuan/penjelasan")

        # Auto validation
        self.auto_validation_var = BooleanVar(
            value=self.config_manager.get_config("auto_validation", True)
        )
        tb.Checkbutton(
            config_frame,
            text="Auto validation before build",
            variable=self.auto_validation_var,
        ).grid(row=1, column=0, columnspan=2, sticky=W, pady=5)

        # Theme
        tb.Label(config_frame, text="Theme:").grid(row=2, column=0, sticky=W)
        self.theme_var = StringVar(
            value=self.config_manager.get_config("theme", "light")
        )
        self.theme_combo = tb.Combobox(
            config_frame,
            textvariable=self.theme_var,
            values=self.theme_manager.get_available_themes(),
            state="readonly",
        )
        self.theme_combo.grid(row=2, column=1, padx=5, sticky=W)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selected)
        btn_theme_help = tb.Button(config_frame, text="?", width=2, command=lambda: self.show_field_help("theme"))
        btn_theme_help.grid(row=2, column=2, sticky=W, padx=2)
        ToolTip(btn_theme_help, "Bantuan/penjelasan")

        # Tombol cek update
        tb.Button(
            config_frame, text="Cek Update", command=self.check_for_updates
        ).grid(row=3, column=0, pady=10, sticky=W)
        self.update_status_var = StringVar(value="Status update: belum dicek")
        self.update_status_label = tb.Label(
            config_frame, textvariable=self.update_status_var
        )
        self.update_status_label.grid(row=3, column=1, columnspan=2, sticky=W)

        # Terapkan warna kontras dengan background theme
        if hasattr(self, "theme_manager"):
            theme = self.theme_manager.get_current_theme()
            style_dict = self.theme_manager.get_style_dict(theme)
            bg = style_dict.get("background", "#fff")

            def is_dark(color):
                color = color.lstrip("#")
                r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
                return (r * 0.299 + g * 0.587 + b * 0.114) < 186

            fg = "#fff" if is_dark(bg) else "#111"
            try:
                self.update_status_label.configure(foreground=fg)
            except Exception:
                pass

        # Theme color settings
        self.colors_frame = tb.LabelFrame(
            settings_frame, text="Theme Colors", padding=10
        )
        self.colors_frame.pack(fill=X, padx=10, pady=5)

        self.color_vars = {}
        color_labels = [
            ("Background", "background"),
            ("Foreground", "foreground"),
            ("Button BG", "button_bg"),
            ("Button FG", "button_fg"),
            ("Accent", "accent"),
        ]
        for i, (label, key) in enumerate(color_labels):
            tb.Label(self.colors_frame, text=label + ":").grid(
                row=i // 2, column=(i % 2) * 3, sticky=W
            )
            var = StringVar()
            self.color_vars[key] = var
            entry = tb.Entry(self.colors_frame, textvariable=var, width=12)
            entry.grid(row=i // 2, column=(i % 2) * 3 + 1, padx=5, sticky=W)
            btn = tb.Button(
                self.colors_frame,
                text="Pilih",
                command=lambda k=key: self.choose_color(k),
            )
            btn.grid(row=i // 2, column=(i % 2) * 3 + 2, padx=2)

        # Action buttons
        self.apply_btn = tb.Button(
            self.colors_frame, text="Apply", command=self.apply_theme_colors
        )
        self.apply_btn.grid(row=3, column=0, pady=5)
        self.reset_btn = tb.Button(
            self.colors_frame, text="Reset", command=self.reset_theme
        )
        self.reset_btn.grid(row=3, column=1, pady=5)
        self.delete_btn = tb.Button(
            self.colors_frame, text="Delete", command=self.delete_theme
        )
        self.delete_btn.grid(row=3, column=2, pady=5)
        self.set_default_btn = tb.Button(
            self.colors_frame, text="Set as Default", command=self.set_as_default_theme
        )
        self.set_default_btn.grid(row=3, column=3, pady=5)

        self.update_theme_color_inputs()
        self.update_theme_action_buttons()

        # Save button
        tb.Button(config_frame, text="Save Settings", command=self.save_settings).grid(
            row=4, column=0, pady=10
        )

    def update_theme_color_inputs(self) -> None:
        theme = self.theme_var.get()
        style = self.theme_manager.get_style_dict(theme)
        for key, var in self.color_vars.items():
            var.set(style.get(key, ""))

    def update_theme_action_buttons(self) -> None:
        theme = self.theme_var.get()
        is_default = theme in self.theme_manager.DEFAULT_THEMES
        is_custom = theme in self.theme_manager.custom_themes
        self.reset_btn.config(state=NORMAL if is_default else DISABLED)
        self.delete_btn.config(state=NORMAL if is_custom else DISABLED)
        self.set_default_btn.config(state=NORMAL if is_default else DISABLED)

    def on_theme_selected(self, event: Optional[Any] = None) -> None:
        theme = self.theme_var.get()
        self.update_theme_color_inputs()
        self.update_theme_action_buttons()
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()

    def choose_color(self, key: str) -> None:
        color = colorchooser.askcolor(
            title=f"Pilih {key.capitalize()}", initialcolor=self.color_vars[key].get()
        )
        if color[1]:
            self.color_vars[key].set(color[1])

    def apply_theme_colors(self) -> None:
        theme = self.theme_var.get()
        style = {k: v.get() for k, v in self.color_vars.items()}
        self.theme_manager.set_theme_colors(theme, style)
        # Persist custom themes
        self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()
        messagebox.showinfo("Success", f"Theme '{theme}' updated.")

    def reset_theme(self) -> None:
        theme = self.theme_var.get()
        self.theme_manager.reset_theme(theme)
        self.update_theme_color_inputs()
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()
        messagebox.showinfo("Reset", f"Theme '{theme}' reset to default.")

    def delete_theme(self) -> None:
        theme = self.theme_var.get()
        if theme in self.theme_manager.custom_themes:
            if messagebox.askyesno("Delete Theme", f"Delete custom theme '{theme}'?"):
                self.theme_manager.delete_custom_theme(theme)
                self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
                # Update dropdown
                self.theme_combo["values"] = self.theme_manager.get_available_themes()
                self.theme_var.set("light")
                self.on_theme_selected()

    def add_theme_dialog(self) -> None:
        dialog = tb.Toplevel(self.root)
        dialog.title("Add Custom Theme")
        dialog.geometry("300x200")
        tb.Label(dialog, text="Theme Name:").pack(pady=5)
        name_var = StringVar()
        tb.Entry(dialog, textvariable=name_var).pack(pady=5)
        color_vars = {}
        color_labels = [
            ("Background", "background", "#282c34"),
            ("Foreground", "foreground", "#abb2bf"),
            ("Button BG", "button_bg", "#3c4048"),
            ("Button FG", "button_fg", "#abb2bf"),
            ("Accent", "accent", "#e06c75"),
        ]
        for label, key, default in color_labels:
            tb.Label(dialog, text=label + ":").pack()
            var = StringVar(value=default)
            color_vars[key] = var
            row = tb.Frame(dialog)
            row.pack()
            tb.Entry(row, textvariable=var, width=12).pack(side=LEFT)
            tb.Button(
                row,
                text="Pilih",
                command=lambda k=key: self._choose_color_dialog(color_vars, k),
            ).pack(side=LEFT)

        def on_add():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Theme name required", parent=dialog)
                return
            if name in self.theme_manager.get_available_themes():
                messagebox.showerror(
                    "Error", "Theme name already exists", parent=dialog
                )
                return
            style = {k: v.get() for k, v in color_vars.items()}
            self.theme_manager.add_custom_theme(name, style)
            self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
            self.theme_combo["values"] = self.theme_manager.get_available_themes()
            self.theme_var.set(name)
            self.on_theme_selected()
            dialog.destroy()

        tb.Button(dialog, text="Add", command=on_add).pack(pady=10)

    def _choose_color_dialog(self, color_vars, key):
        color = colorchooser.askcolor(
            title=f"Pilih {key.capitalize()}", initialcolor=color_vars[key].get()
        )
        if color[1]:
            color_vars[key].set(color[1])

    def setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = tb.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Report", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(
            label="Project Analysis", command=lambda: self.notebook.select(2)
        )
        tools_menu.add_command(
            label="Project Validation", command=lambda: self.notebook.select(3)
        )
        tools_menu.add_command(
            label="Project Templates", command=lambda: self.notebook.select(1)
        )

        # Help menu
        help_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        self.root.config(menu=menubar)

        # Project menu (only if beta features are enabled)
        if self.config_manager.get_config(
            "enable_beta_features", False
        ) and self.config_manager.get_config("enable_project_wizard_beta", False):
            project_menu = tb.Menu(menubar, tearoff=0)
            project_menu.add_command(
                label="Project Wizard (Beta)", command=self.open_project_wizard
            )
            menubar.add_cascade(label="Project", menu=project_menu)

    # Event handlers
    def browse_file(self) -> None:
        """Browse file dan validasi file Python."""
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            if not os.path.isfile(file_path):
                messagebox.showerror("File Error", "File tidak ditemukan.")
                return
            if not file_path.endswith(".py"):
                messagebox.showerror("File Error", "File harus berekstensi .py.")
                return
            self.file_path_var.set(file_path)
            self.current_project_path = str(Path(file_path).parent)

    def browse_output_dir(self) -> None:
        """Browse dan validasi output directory."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            if not os.path.isdir(dir_path):
                messagebox.showerror("Folder Error", "Folder tidak ditemukan.")
                return
            self.output_dir_var.set(dir_path)

    def browse_project_output(self):
        """Buka dialog untuk memilih folder output project baru."""
        path = filedialog.askdirectory(title="Pilih Folder Output Project")
        if path:
            self.project_path_var.set(path)

    def browse_analysis_path(self) -> None:
        """Browse dan validasi analysis path."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            if not os.path.isdir(dir_path):
                messagebox.showerror("Folder Error", "Folder tidak ditemukan.")
                return
            self.analysis_path_var.set(dir_path)

    def browse_validation_path(self) -> None:
        """Browse dan validasi validation path."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            if not os.path.isdir(dir_path):
                messagebox.showerror("Folder Error", "Folder tidak ditemukan.")
                return
            self.validation_path_var.set(dir_path)

    def browse_default_output(self) -> None:
        """Browse for default output directory."""
        directory = filedialog.askdirectory(title="Select Default Output Directory")
        if directory:
            self.default_output_var.set(directory)

    def on_template_selected(self, event: Any) -> None:
        """Handle template selection."""
        template_name = self.template_var.get()
        if template_name:
            template_info = self.builder.get_template_info(template_name)
            if template_info:
                info_text = f"""Template: {template_info.name}
Description: {template_info.description}
Entry Point: {template_info.entry_point}
Dependencies: {', '.join(template_info.dependencies)}
Additional Files: {', '.join(template_info.additional_files)}
"""
                self.template_info_text.delete(1.0, END)
                self.template_info_text.insert(1.0, info_text)

    def create_project(self) -> None:
        """Create new project from template."""
        project_name = self.project_name_var.get().strip()
        template_name = self.template_var.get()
        output_path = self.project_path_var.get().strip()
        gui_library = self.gui_library_var.get()
        backend = self.backend_var.get()
        database = self.database_var.get()
        testing = self.testing_var.get()
        utility = self.utility_var.get()
        custom_projectrules = self.custom_projectrules
        custom_background = self.custom_background
        if not all([project_name, template_name, output_path]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        try:
            result = self.builder.create_project_from_template(
                project_name, template_name, output_path,
                gui_library, backend, database, testing, utility,
                custom_projectrules, custom_background
            )
            if result["success"]:
                messagebox.showinfo(
                    "Success",
                    f"Project created successfully!\nPath: {result['project_path']}",
                )
                self.analysis_path_var.set(result["project_path"])
                self.validation_path_var.set(result["project_path"])
                self.notebook.select(0)  # Tab dashboard
            else:
                messagebox.showerror("Error", result.get("error", "Unknown error"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}")

    def start_build(self) -> None:
        """Start build process dengan custom args."""
        if hasattr(self, "build_in_progress") and self.build_in_progress:
            messagebox.showwarning("Build Sedang Berjalan", "Hanya satu build yang boleh aktif dalam satu waktu. Tunggu proses build selesai atau cancel terlebih dahulu.", parent=self.root)
            return
        self.build_in_progress = True
        file_path = self.file_path_var.get()
        output_format = self.format_var.get()
        output_dir = self.output_dir_var.get()
        custom_args = self.custom_args_var.get().strip()
        if not file_path or not output_format or not output_dir:
            messagebox.showerror("Input Error", "Lengkapi semua input build.")
            self.build_in_progress = False
            return
        self.progress_var.set("Building...")
        self.progress_bar.start()
        self.build_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        # Jalankan build di thread terpisah
        self.build_thread = threading.Thread(
            target=self._build_thread,
            args=(file_path, output_format, output_dir, custom_args),
            daemon=True,
        )
        self.build_thread.start()

    def start_build_with_validation(self, file_path: str, output_format: str) -> None:
        """Start build with validation."""
        self.build_thread = threading.Thread(
            target=self._build_with_validation_thread, args=(file_path, output_format)
        )
        self.build_thread.start()

        self.build_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Building with validation...")

    def start_normal_build(self, file_path: str, output_format: str) -> None:
        """Start normal build."""
        self.build_thread = threading.Thread(
            target=self._build_thread, args=(file_path, output_format)
        )
        self.build_thread.start()

        self.build_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Building...")

    def _build_with_validation_thread(self, file_path: str, output_format: str) -> None:
        """Build thread with validation."""
        try:
            project_path = str(Path(file_path).parent)
            result = self.builder.build_with_validation(project_path, output_format)

            self.root.after(0, self._build_completed, result)

        except Exception as e:
            self.root.after(0, self._build_error, str(e))

    def _build_thread(
        self, file_path: str, output_format: str, output_dir: str, custom_args: str
    ) -> None:
        try:
            # Gunakan builder.get_final_build_args untuk argumen build final
            project_dir = str(Path(file_path).parent)
            final_args = self.builder.get_final_build_args(project_dir, output_format, custom_args)
            if output_dir:
                self.builder.output_directory = output_dir
            result = self.builder.build(file_path, output_format, final_args)
            self.root.after(0, lambda: self._build_completed(result))
        except Exception as e:
            self.root.after(0, lambda: self._build_error(str(e)))

    def _build_completed(self, result: Any) -> None:
        self.progress_bar.stop()
        self.build_button.config(state=NORMAL)
        self.cancel_button.config(state=DISABLED)
        self.progress_var.set("Ready")
        self.build_in_progress = False
        # Tampilkan log detail build di UI
        self.log_text.insert(END, f"Build selesai: {result}\n")
        if hasattr(result, "log_output") and result.log_output:
            self.log_text.insert(END, f"\n=== Build Log ===\n{result.log_output}\n")
        self.status_bar.config(text="Build Sukses", foreground="green")
        try:
            self.root.bell()  # Sound notification
        except Exception:
            pass
        messagebox.showinfo(
            "Build Sukses", f"Build selesai: {result}", parent=self.root
        )
        self.log_text.see(END)
        # Tambahkan tombol export log setelah build selesai
        self.add_export_log_button()

    def _build_error(self, error: str) -> None:
        self.progress_bar.stop()
        self.build_button.config(state=NORMAL)
        self.cancel_button.config(state=DISABLED)
        self.progress_var.set("Ready")
        self.build_in_progress = False
        self.log_text.insert(END, f"Build gagal: {error}\n")
        self.status_bar.config(text="Build Gagal", foreground="red")
        try:
            self.root.bell()  # Sound notification
        except Exception:
            pass
        messagebox.showerror("Build Gagal", f"Build gagal: {error}", parent=self.root)
        self.log_text.see(END)
        self.add_export_log_button()

    def add_export_log_button(self):
        # Tambahkan tombol export/copy log jika belum ada
        parent_frame = self.log_text.master  # log_frame
        if not hasattr(self, "export_log_button") or not self.export_log_button.winfo_exists():
            self.export_log_button = tb.Button(
                parent_frame,
                text="Export Log",
                command=self.export_log_to_file,
                width=12,
            )
            self.export_log_button.pack(side="right", padx=8, pady=4)

    def export_log_to_file(self):
        # Export isi log_text ke file
        from tkinter import filedialog
        log_content = self.log_text.get(1.0, END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Simpan Build Log"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                messagebox.showinfo("Export Log", f"Log berhasil disimpan ke: {file_path}")
            except Exception as e:
                messagebox.showerror("Export Log", f"Gagal menyimpan log: {e}")

    def cancel_build(self) -> None:
        """Cancel build process."""
        if self.builder.cancel_build():
            self.progress_bar.stop()
            self.build_button.config(state=NORMAL)
            self.cancel_button.config(state=DISABLED)
            self.progress_var.set("Build cancelled")
            self.log_text.insert(END, "\nBuild cancelled by user\n")
            self.build_in_progress = False

    def analyze_project(self) -> None:
        """Analyze project dependencies."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            analysis = self.builder.analyze_project(project_path)

            if "error" in analysis:
                self.analysis_text.delete(1.0, END)
                self.analysis_text.insert(1.0, f"Error: {analysis['error']}")
            else:
                report = self.builder.generate_project_report(project_path)
                self.analysis_text.delete(1.0, END)
                self.analysis_text.insert(1.0, report)

        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")

    def generate_requirements(self) -> None:
        """Generate requirements.txt."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            success = self.builder.dependency_analyzer.generate_requirements_txt(
                project_path
            )
            if success:
                messagebox.showinfo(
                    "Success", "requirements.txt generated successfully!"
                )
            else:
                messagebox.showerror("Error", "Failed to generate requirements.txt")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate requirements: {e}")

    def validate_dependencies(self) -> None:
        """Validate project dependencies."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            validation = self.builder.dependency_analyzer.validate_dependencies(
                project_path
            )

            if validation.get("valid", False):
                messagebox.showinfo("Success", "All dependencies are valid!")
            else:
                missing = validation.get("missing_dependencies", [])
                messagebox.showwarning(
                    "Warning", f"Missing dependencies: {', '.join(missing)}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")

    def validate_structure(self) -> None:
        """Validate project structure."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            validation = self.builder.build_validator.validate_project_structure(
                project_path
            )

            report = self.builder.build_validator.get_validation_report(project_path)
            self.validation_text.delete(1.0, END)
            self.validation_text.insert(1.0, report)

            if validation.get("valid", False):
                messagebox.showinfo("Success", "Project structure is valid!")
            else:
                messagebox.showwarning("Warning", "Project structure has issues")

        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")

    def generate_report(self) -> None:
        """Generate comprehensive project report."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            report = self.builder.generate_project_report(project_path)
            self.validation_text.delete(1.0, END)
            self.validation_text.insert(1.0, report)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def fix_structure(self) -> None:
        """Fix project structure."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return

        try:
            success = self.builder.build_validator.generate_project_structure(
                project_path
            )
            if success:
                messagebox.showinfo("Success", "Project structure fixed!")
                self.validate_structure()  # Refresh validation
            else:
                messagebox.showerror("Error", "Failed to fix project structure")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fix structure: {e}")

    def save_settings(self) -> None:
        """Simpan pengaturan, termasuk status fitur beta dan wizard beta, lalu refresh tab Project Templates jika perlu."""
        config = self.config_manager.load_config()
        config["theme"] = self.theme_var.get()
        config["default_output_dir"] = self.default_output_var.get()
        config["auto_validation"] = self.auto_validation_var.get()
        # Simpan custom themes jika ada perubahan
        config["custom_themes"] = self.theme_manager.custom_themes
        config["default_theme_overrides"] = self.theme_manager.default_theme_overrides
        self.config_manager.save_config(config)
        messagebox.showinfo("Success", "Settings saved successfully!")

        # Perbaikan: Jangan hapus dan tambah ulang tab Project Templates
        # Jika perlu update tombol wizard, lakukan update pada frame/tab yang sudah ada
        # (Implementasi update dinamis bisa ditambahkan di sini jika perlu)

    def open_project(self) -> None:
        """Open existing project."""
        directory = filedialog.askdirectory(title="Open Project")
        if directory:
            self.analysis_path_var.set(directory)
            self.validation_path_var.set(directory)
            self.notebook.select(2)  # Switch to analysis tab

    def save_report(self) -> None:
        """Save current report."""
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filename:
            try:
                # Get current tab content
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 2:  # Analysis tab
                    content = self.analysis_text.get(1.0, END)
                elif current_tab == 3:  # Validation tab
                    content = self.validation_text.get(1.0, END)
                else:
                    content = self.log_text.get(1.0, END)

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

                messagebox.showinfo("Success", "Report saved successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def show_about(self) -> None:
        """Show about dialog."""
        about_text = """PyCraft Studio - Enhanced

A Python GUI application for building Python scripts into executables.

Features:
- Project templates
- Dependency analysis
- Project validation
- Enhanced build process
- Comprehensive reporting

Version: 2.0.0
"""
        messagebox.showinfo("About", about_text)

    def update_widget_themes(self) -> None:
        """Update warna widget non-ttk agar sesuai tema aktif."""
        style_dict = self.theme_manager.get_style_dict(
            self.theme_manager.get_current_theme()
        )
        for widget in self.themable_widgets:
            try:
                widget.configure(
                    bg=style_dict["background"], fg=style_dict["foreground"]
                )
            except Exception:
                pass
        # Force refresh ttk styles
        self.root.update_idletasks()

    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()

    def set_as_default_theme(self) -> None:
        theme = self.theme_var.get()
        if theme in self.theme_manager.DEFAULT_THEMES:
            if messagebox.askyesno(
                "Set as Default",
                f"Yakin ingin mengubah default untuk theme '{theme}'?\nTindakan ini akan mengubah default reset theme.",
            ):
                style = {k: v.get() for k, v in self.color_vars.items()}
                self.theme_manager.set_default_theme(theme, style)
                self.config_manager.set_default_theme_overrides(
                    self.theme_manager.default_theme_overrides
                )
                messagebox.showinfo(
                    "Set as Default", f"Default untuk theme '{theme}' berhasil diubah."
                )

    def open_project_wizard(self) -> None:
        """Buka wizard step-by-step pembuatan project baru."""
        wizard = tb.Toplevel(self.root)
        wizard.title("Wizard Project Baru")
        wizard.geometry("500x400")
        wizard.transient(self.root)
        wizard.grab_set()

        steps = [
            "Pilih Template",
            "Nama Project",
            "Lokasi Output",
            "Preview Struktur",
            "Konfirmasi",
        ]
        current_step = IntVar(value=0)

        # State
        selected_template = StringVar()
        project_name = StringVar()
        output_path = StringVar()
        preview_text = StringVar()
        result_text = StringVar()

        def update_step():
            for frame in step_frames:
                frame.pack_forget()
            step_frames[current_step.get()].pack(
                fill=BOTH, expand=True, padx=10, pady=10
            )
            step_label.config(
                text=f"Step {current_step.get()+1}: {steps[current_step.get()]}"
            )

        def next_step():
            if current_step.get() < len(steps) - 1:
                current_step.set(current_step.get() + 1)
                update_step()

        def prev_step():
            if current_step.get() > 0:
                current_step.set(current_step.get() - 1)
                update_step()

        def do_preview():
            # Preview struktur project (sederhana)
            name = project_name.get() or "my_project"
            template = selected_template.get() or "console"
            preview = f"{name}/\n  src/\n    main.py\n  requirements.txt\n  README.md\n  (template: {template})"
            preview_text.set(preview)
            next_step()

        def do_create():
            # Panggil builder
            name = project_name.get()
            template = selected_template.get()
            out_path = output_path.get()
            if not name or not template or not out_path:
                result_text.set("Lengkapi semua data!")
                return
            result = self.builder.create_project_from_template(name, template, out_path)
            if result.get("success"):
                result_text.set(
                    f"Project berhasil dibuat di {result.get('project_path')}"
                )
                messagebox.showinfo(
                    "Sukses", f"Project berhasil dibuat di {result.get('project_path')}"
                )
                wizard.destroy()
            else:
                result_text.set(f"Gagal: {result.get('error')}")
                messagebox.showerror(
                    "Gagal", f"Gagal membuat project: {result.get('error')}"
                )

        # Step frames
        step_frames = []
        # Step 1: Pilih Template
        frame1 = tb.Frame(wizard)
        tb.Label(frame1, text="Pilih Template:").pack(anchor=W, pady=5)
        templates = self.builder.get_available_templates()
        tb.Combobox(
            frame1, textvariable=selected_template, values=templates, state="readonly"
        ).pack(fill=X)
        step_frames.append(frame1)
        # Step 2: Nama Project
        frame2 = tb.Frame(wizard)
        tb.Label(frame2, text="Nama Project:").pack(anchor=W, pady=5)
        tb.Entry(frame2, textvariable=project_name).pack(fill=X)
        step_frames.append(frame2)
        # Step 3: Lokasi Output
        frame3 = tb.Frame(wizard)
        tb.Label(frame3, text="Lokasi Output:").pack(anchor=W, pady=5)
        out_entry = tb.Entry(frame3, textvariable=output_path)
        out_entry.pack(fill=X, side=LEFT, expand=True)

        def browse_out():
            path = filedialog.askdirectory()
            if path:
                output_path.set(path)

        tb.Button(frame3, text="📁", command=browse_out, width=2).pack(side=LEFT, padx=5)
        step_frames.append(frame3)
        # Step 4: Preview Struktur
        frame4 = tb.Frame(wizard)
        tb.Label(frame4, text="Preview Struktur Project:").pack(anchor=W, pady=5)
        tb.Label(
            frame4,
            textvariable=preview_text,
            background="#f0f0f0",
            relief=SUNKEN,
            anchor=W,
            justify=LEFT,
        ).pack(fill=BOTH, expand=True)
        step_frames.append(frame4)
        # Step 5: Konfirmasi & Create
        frame5 = tb.Frame(wizard)
        tb.Label(frame5, text="Konfirmasi & Create Project").pack(anchor=W, pady=5)
        tb.Label(frame5, textvariable=result_text, foreground="blue").pack(
            anchor=W, pady=5
        )
        tb.Button(frame5, text="Buat Project", command=do_create).pack(pady=10)
        step_frames.append(frame5)

        # Step navigation
        nav_frame = tb.Frame(wizard)
        nav_frame.pack(side=BOTTOM, fill=X, pady=5)
        step_label = tb.Label(nav_frame, text="Step 1: Pilih Template")
        step_label.pack(side=LEFT, padx=5)
        tb.Button(nav_frame, text="< Sebelumnya", command=prev_step).pack(
            side=LEFT, padx=5
        )

        def next_or_preview():
            if current_step.get() == 2:
                do_preview()
            elif current_step.get() < len(steps) - 1:
                next_step()

        tb.Button(nav_frame, text="Selanjutnya >", command=next_or_preview).pack(
            side=LEFT, padx=5
        )
        tb.Button(nav_frame, text="Tutup", command=wizard.destroy).pack(
            side=RIGHT, padx=5
        )

        update_step()

    def check_for_updates(self) -> None:
        """Cek versi terbaru dari GitHub Releases dan bandingkan dengan versi lokal."""
        repo_api = "https://api.github.com/repos/fajarkurnia0388/pycraft-studio/releases/latest"
        try:
            with open("VERSION", "r") as f:
                local_version = f.read().strip()
        except Exception:
            local_version = "unknown"
        try:
            with urllib.request.urlopen(repo_api, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name") or data.get("name")
                html_url = data.get("html_url")
                if latest_version and local_version != latest_version:
                    msg = f"Versi terbaru tersedia: {latest_version}\nVersi lokal: {local_version}\nDownload: {html_url}"
                    self.update_status_var.set(f"Update tersedia: {latest_version}")
                    messagebox.showinfo("Update Tersedia", msg)
                else:
                    self.update_status_var.set(
                        f"Aplikasi sudah versi terbaru: {local_version}"
                    )
                    messagebox.showinfo(
                        "Up to Date", f"Aplikasi sudah versi terbaru: {local_version}"
                    )
        except Exception as e:
            self.update_status_var.set(f"Gagal cek update: {e}")
            messagebox.showerror("Cek Update Gagal", f"Gagal cek update: {e}")

    def validate_conflicts(self):
        gui = self.gui_library_var.get()
        backend = self.backend_var.get()
        database = self.database_var.get()
        testing = self.testing_var.get()
        utility = self.utility_var.get()
        # 1. Semua None
        if all(x == "None" for x in [gui, backend, database, testing, utility]):
            messagebox.showwarning(
                "Kombinasi Tidak Valid",
                "Tidak boleh semua library None. Pilih minimal satu library.",
                parent=self.root,
            )
            return False
        # 2. GUI desktop + backend web
        backend_webs = ["Flask", "FastAPI", "Django", "Starlette", "Quart", "Tornado"]
        gui_desktops = ["tkinter", "customtkinter", "PyQt", "PySide", "wxPython"]
        if gui in gui_desktops and backend in backend_webs:
            messagebox.showwarning(
                "Kombinasi Tidak Umum",
                f"Kombinasi {gui} (desktop) + {backend} (backend web) jarang dipakai bersama. Pastikan memang dibutuhkan.",
                parent=self.root,
            )
            return False
        # 3. Database MongoDB dengan GUI tkinter/customtkinter
        if database == "MongoDB" and gui in ["tkinter", "customtkinter"]:
            messagebox.showwarning(
                "Kombinasi Tidak Umum",
                f"Kombinasi {gui} + MongoDB jarang digunakan. Biasanya MongoDB dipakai untuk aplikasi web atau backend.",
                parent=self.root,
            )
            return False
        # 4. Utility CLI tanpa backend/GUI
        if utility in ["typer", "click"] and gui == backend == "None":
            messagebox.showwarning(
                "Kombinasi Tidak Umum",
                f"Utility CLI ({utility}) tanpa backend/GUI kurang bermanfaat. Biasanya CLI dipakai untuk API atau aplikasi desktop.",
                parent=self.root,
            )
            return False
        return True

    # Panggil validasi ini setiap kali selector berubah
    def show_template_and_chemistry(self):
        if not self.validate_conflicts():
            return
        self.on_template_selected(None)
        self.update_chemistry_comment()

    def show_field_help(self, key):
        help_texts = {
            # Project Template
            "project_name": "Nama project baru Anda. Gunakan huruf, angka, dan underscore. Hindari spasi dan karakter spesial.",
            "template": "Template project menentukan struktur awal dan dependensi project Anda.",
            "output_path": "Folder tujuan project baru akan dibuat. Pastikan folder writable.",
            "gui_library": "Pilih library GUI utama untuk aplikasi Anda. Klik ? untuk info detail tiap library.",
            "backend": "Pilih library backend (opsional) jika ingin aplikasi terhubung ke server/API.",
            "database": "Pilih database yang akan digunakan aplikasi (opsional).",
            "testing": "Pilih library testing untuk pengujian otomatis (opsional).",
            "utility": "Pilih library utility (CLI, logging, dsb) untuk fitur tambahan (opsional).",
            # Build
            "file_path": "File Python utama yang akan dibuild menjadi executable.",
            "output_dir": "Folder hasil build. Semua file hasil build akan disimpan di sini.",
            "custom_args": "Argumen tambahan untuk builder, misal: --icon, --hidden-import, dsb.",
            # Settings
            "default_output": "Folder default untuk hasil build project baru.",
            "theme": "Pilih tema tampilan aplikasi (light/dark/custom).",
            # Analysis/Validation
            "analysis_path": "Path ke folder project Python yang ingin dianalisis dependency-nya.",
            "validation_path": "Path ke folder project Python yang ingin divalidasi strukturnya.",
        }
        msg = help_texts.get(key, "Tidak ada info.")
        messagebox.showinfo("Info", msg, parent=self.root)

    def show_custom_args_almanak(self):
        """Tampilkan almanak argumen populer untuk custom build args."""
        info = [
            (
                "--icon",
                "Set icon aplikasi (misal: .ico/.icns)",
                "Agar hasil build punya icon khusus",
            ),
            (
                "--add-data",
                "Copy file/folder ke hasil build (src:dst)",
                "Untuk menyertakan resource tambahan",
            ),
            (
                "--hidden-import",
                "Tambahkan modul tersembunyi",
                "Jika ada import dinamis yang tidak terdeteksi otomatis",
            ),
            (
                "--noconsole",
                "Sembunyikan console window (Windows)",
                "Untuk aplikasi GUI tanpa jendela terminal",
            ),
            (
                "--windowed",
                "Jalankan sebagai aplikasi GUI (Windows/Mac)",
                "Agar tidak muncul terminal saat run",
            ),
            (
                "--onefile",
                "Bundle jadi 1 file executable",
                "Distribusi lebih mudah, file tunggal",
            ),
            (
                "--onedir",
                "Bundle jadi 1 folder",
                "Debugging lebih mudah, file terpisah",
            ),
            ("--clean", "Bersihkan hasil build sebelumnya", "Agar build selalu fresh"),
            (
                "--noupx",
                "Jangan kompres dengan UPX",
                "Kadang diperlukan jika UPX bermasalah",
            ),
            (
                "--strip",
                "Hapus symbol debug",
                "Ukuran file lebih kecil, tidak bisa debug",
            ),
        ]
        win = tb.Toplevel(self.root)
        win.title("Info Detail Custom Build Args")
        win.geometry("700x350")
        win.transient(self.root)
        win.grab_set()
        frame = tb.Frame(win, padding=14)
        frame.pack(fill=BOTH, expand=True)
        header = tb.Label(
            frame,
            text="Info Detail Argumen Populer Builder",
            font=("Arial", 14, "bold"),
        )
        header.pack(anchor=W, pady=(0, 6))
        desc = tb.Label(
            frame,
            text="Penjelasan singkat argumen populer untuk builder (misal: PyInstaller).",
            foreground="gray",
            font=("Arial", 10),
        )
        desc.pack(anchor=W, pady=(0, 10))
        columns = ("Argumen", "Deskripsi", "Keterangan")
        style = tb.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure(
            "Treeview", rowheight=32, font=("Arial", 10), borderwidth=1, relief="solid"
        )
        tree = tb.Treeview(frame, columns=columns, show="headings", height=8)
        for col, w in zip(columns, [120, 320, 200]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=W, stretch=True)
        for idx, (arg, desc_, ket) in enumerate(info):
            tree.insert(
                "",
                END,
                values=(arg, desc_, ket),
                tags=("oddrow" if idx % 2 else "evenrow",),
            )
        tree.tag_configure("oddrow", background="#f7f7f7")
        tree.tag_configure("evenrow", background="#ffffff")
        tree.pack(fill=BOTH, expand=True, pady=4, padx=2)
        scrollbar = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 4))
        tb.Button(frame, text="Tutup", command=win.destroy).pack(pady=(12, 16))

    def show_multiplatform_almanak(self):
        """Tampilkan panduan lengkap build multiplatform via GitHub Actions (dengan contoh)."""
        info = (
            "Panduan Build Multiplatform (exe/app/binary) via GitHub Actions\n\n"
            "=== Step-by-Step ===\n"
            "1. Pastikan repo GitHub Anda sudah memiliki file workflow build multiplatform.\n"
            "   Contoh: .github/workflows/build-multiplatform.yml\n\n"
            "2. Contoh isi file workflow:\n"
            "---------------------------------------------\n"
            "name: Build & Release Multiplatform\n"
            "on:\n  push:\n    tags:\n      - 'v*.*.*'\n"
            "jobs:\n  build:\n    runs-on: ${{ matrix.os }}\n    strategy:\n      matrix:\n        os: [ubuntu-latest, windows-latest, macos-latest]\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n      - run: pip install pyinstaller\n      - run: pyinstaller --onefile src/main.py --name PyCraftStudio\n      - run: mkdir release && cp README.md LICENSE release/ || echo 'No README/LICENSE'\n      - run: cp -r docs release/ || echo 'No docs'\n      - run: cp dist/PyCraftStudio* release/\n      - run: zip -r PyCraftStudio-${{ runner.os }}.zip release/\n        if: runner.os != 'Windows'\n      - run: Compress-Archive -Path release\\* -DestinationPath PyCraftStudio-Windows.zip\n        if: runner.os == 'Windows'\n      - uses: actions/upload-artifact@v4\n        with:\n          name: PyCraftStudio-${{ runner.os }}\n          path: PyCraftStudio-*.zip\n  release:\n    needs: build\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/download-artifact@v4\n        with:\n          path: artifacts\n      - uses: softprops/action-gh-release@v2\n        with:\n          files: artifacts/**/PyCraftStudio-*.zip\n        env:\n          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n"
            "---------------------------------------------\n\n"
            "3. Commit dan push semua perubahan ke GitHub:\n"
            "   git add .\n   git commit -m 'release: v1.2.0'\n   git push\n\n"
            "4. Buat dan push tag versi baru:\n"
            "   git tag v1.2.0\n   git push --tags\n\n"
            "5. Workflow GitHub Actions akan otomatis berjalan di Windows, Linux, dan macOS.\n"
            "   Cek status di tab Actions di GitHub repo Anda.\n\n"
            "6. Setelah workflow selesai, hasil build (ZIP/exe/app/binary) akan tersedia di halaman Releases GitHub.\n"
            "   Contoh hasil release:\n"
            "   - PyCraftStudio-ubuntu-latest.zip\n   - PyCraftStudio-windows-latest.zip\n   - PyCraftStudio-macos-latest.zip\n\n"
            "=== Tips & Troubleshooting ===\n"
            "- Pastikan file entry-point (src/main.py) benar dan bisa dijalankan.\n"
            "- Semua dependensi harus ada di requirements.txt.\n"
            "- Untuk build macOS, hindari library khusus Windows/Linux.\n"
            "- Jika build gagal, klik tab Actions → pilih job yang gagal → cek log error.\n"
            "- Untuk build custom (misal: argumen PyInstaller), edit bagian 'run: pyinstaller ...' di workflow.\n"
            "- Jika ingin build otomatis setiap push ke branch tertentu, ubah bagian 'on:' di workflow.\n\n"
            "=== Referensi & Bantuan ===\n"
            "- Dokumentasi GitHub Actions: https://docs.github.com/en/actions\n"
            "- Dokumentasi PyInstaller: https://pyinstaller.org/en/stable/\n"
            "- Contoh workflow lain: https://github.com/actions/starter-workflows\n\n"
            "Jika butuh bantuan lebih lanjut, hubungi maintainer atau tim devops Anda.\n"
        )
        win = tb.Toplevel(self.root)
        win.title("Panduan Build Multiplatform")
        win.geometry("800x600")
        win.transient(self.root)
        win.grab_set()
        frame = tb.Frame(win, padding=14)
        frame.pack(fill=BOTH, expand=True)
        header = tb.Label(
            frame,
            text="Panduan Lengkap Build Multiplatform via GitHub Actions",
            font=("Arial", 14, "bold"),
        )
        header.pack(anchor=W, pady=(0, 6))
        text = scrolledtext.ScrolledText(
            frame, height=32, wrap=WORD, font=("Consolas", 10)
        )
        text.insert(END, info)
        text.config(state=DISABLED)
        text.pack(fill=BOTH, expand=True, pady=4, padx=2)
        tb.Button(frame, text="Tutup", command=win.destroy).pack(pady=(12, 16))

# Helper class untuk tooltip universal
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font="tahoma 9 normal")
        label.pack(ipadx=6, ipady=2)
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
