"""
Tujuan: Interface GUI utama untuk aplikasi PyCraft Studio
Dependensi: tkinter, threading, queue
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: app = MainWindow().run()
"""

import logging
import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from src.core.builder import BuildResult, ProjectBuilder
from src.core.config import ConfigManager
from src.utils.file_utils import FileValidator

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Window utama aplikasi PyCraft Studio.

    Menyediakan interface GUI yang modern dengan progress tracking,
    error handling, dan konfigurasi yang persisten.
    """

    def __init__(self):
        """Inisialisasi MainWindow."""
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.builder: Optional[ProjectBuilder] = None
        self.build_thread: Optional[threading.Thread] = None
        self.log_queue = queue.Queue()

        self._setup_window()
        self._create_widgets()
        self._load_config()
        self._setup_logging()

    def _setup_window(self):
        """Setup window utama."""
        self.root.title("PyCraft Studio - Python Project Builder")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Set minimum size
        self.root.minsize(600, 500)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        self.root.configure(bg="#f0f0f0")

    def _create_widgets(self):
        """Membuat dan menata widget."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="PyCraft Studio", font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Project selection section
        self._create_project_section(main_frame)

        # Build options section
        self._create_build_options_section(main_frame)

        # Build control section
        self._create_build_control_section(main_frame)

        # Progress section
        self._create_progress_section(main_frame)

        # Log section
        self._create_log_section(main_frame)

        # Status bar
        self._create_status_bar(main_frame)

    def _create_project_section(self, parent):
        """Membuat section pemilihan proyek."""
        # Project frame
        project_frame = ttk.LabelFrame(parent, text="Pemilihan Proyek", padding="10")
        project_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        project_frame.columnconfigure(1, weight=1)

        # Project path
        ttk.Label(project_frame, text="File Python:").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.project_path_var = tk.StringVar()
        project_entry = ttk.Entry(
            project_frame, textvariable=self.project_path_var, width=50
        )
        project_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        browse_btn = ttk.Button(
            project_frame, text="Browse", command=self._browse_project
        )
        browse_btn.grid(row=1, column=2, padx=(5, 0))

        # File info
        self.file_info_label = ttk.Label(project_frame, text="", foreground="gray")
        self.file_info_label.grid(row=2, column=0, columnspan=3, sticky="w")

    def _create_build_options_section(self, parent):
        """Membuat section opsi build."""
        # Options frame
        options_frame = ttk.LabelFrame(parent, text="Opsi Build", padding="10")
        options_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Output format
        ttk.Label(options_frame, text="Format Output:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        self.output_format_var = tk.StringVar(value="exe")
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        self.exe_radio = ttk.Radiobutton(
            format_frame,
            text="Windows (.exe)",
            variable=self.output_format_var,
            value="exe",
        )
        self.exe_radio.grid(row=0, column=0, padx=(0, 10))

        self.app_radio = ttk.Radiobutton(
            format_frame,
            text="macOS (.app)",
            variable=self.output_format_var,
            value="app",
        )
        self.app_radio.grid(row=0, column=1, padx=(0, 10))

        self.binary_radio = ttk.Radiobutton(
            format_frame,
            text="Linux (binary)",
            variable=self.output_format_var,
            value="binary",
        )
        self.binary_radio.grid(row=0, column=2)

        # Additional options
        self.console_var = tk.BooleanVar(value=False)
        console_check = ttk.Checkbutton(
            options_frame, text="Tampilkan console window", variable=self.console_var
        )
        console_check.grid(row=2, column=0, sticky=tk.W)

    def _create_build_control_section(self, parent):
        """Membuat section kontrol build."""
        # Control frame
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))

        # Build button
        self.build_btn = ttk.Button(
            control_frame,
            text="Build Proyek",
            command=self._start_build,
            style="Accent.TButton",
        )
        self.build_btn.grid(row=0, column=0, padx=(0, 10))

        # Cancel button
        self.cancel_btn = ttk.Button(
            control_frame, text="Batal", command=self._cancel_build, state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1)

    def _create_progress_section(self, parent):
        """Membuat section progress."""
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        progress_frame.columnconfigure(0, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Siap untuk build...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)

    def _create_log_section(self, parent):
        """Membuat section log."""
        # Log frame
        log_frame = ttk.LabelFrame(parent, text="Log Build", padding="10")
        log_frame.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, width=80, font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Log control frame
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Clear log button
        clear_btn = ttk.Button(
            log_control_frame, text="Clear Log", command=self._clear_log
        )
        clear_btn.grid(row=0, column=0)

        # Save log button
        save_btn = ttk.Button(
            log_control_frame, text="Save Log", command=self._save_log
        )
        save_btn.grid(row=0, column=1, padx=(5, 0))

    def _create_status_bar(self, parent):
        """Membuat status bar."""
        # Status frame
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        # Status label
        self.status_label = ttk.Label(status_frame, text="Siap", relief=tk.SUNKEN)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _load_config(self):
        """Memuat konfigurasi."""
        config = self.config_manager.load_config()
        self.project_path_var.set(config.get("last_project", ""))
        self.output_format_var.set(config.get("output_format", "exe"))

        # Update file info if project exists
        if self.project_path_var.get():
            self._update_file_info()

    def _setup_logging(self):
        """Setup logging untuk GUI."""
        # Start log processing thread
        self.log_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.log_thread.start()

    def _browse_project(self):
        """Membuka dialog untuk memilih file proyek."""
        file_path = filedialog.askopenfilename(
            title="Pilih File Python",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
        )

        if file_path:
            self.project_path_var.set(file_path)
            self._update_file_info()
            self._save_config()

    def _update_file_info(self):
        """Update informasi file yang dipilih."""
        file_path = self.project_path_var.get()
        if file_path:
            if FileValidator.is_valid_python_file(file_path):
                from src.utils.file_utils import FileManager

                file_info = FileManager.get_file_info(file_path)
                if file_info:
                    size_mb = file_info["size"] / (1024 * 1024)
                    self.file_info_label.config(
                        text=f"File: {file_info['name']} ({size_mb:.2f} MB)",
                        foreground="green",
                    )
                else:
                    self.file_info_label.config(
                        text="File tidak dapat dibaca", foreground="red"
                    )
            else:
                self.file_info_label.config(
                    text="File Python tidak valid", foreground="red"
                )
        else:
            self.file_info_label.config(text="", foreground="gray")

    def _start_build(self):
        """Memulai proses build."""
        if not self.project_path_var.get():
            messagebox.showerror("Error", "Pilih file proyek Python terlebih dahulu!")
            return

        if not FileValidator.is_valid_python_file(self.project_path_var.get()):
            messagebox.showerror("Error", "File Python tidak valid!")
            return

        # Disable build button, enable cancel button
        self.build_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

        # Reset progress
        self.progress_var.set(0)
        self.progress_label.config(text="Memulai build...")
        self.status_label.config(text="Building...")

        # Start build in separate thread
        self.builder = ProjectBuilder()
        self.build_thread = threading.Thread(target=self._build_worker, daemon=True)
        self.build_thread.start()

    def _build_worker(self):
        """Worker thread untuk proses build."""
        try:
            # Prepare additional arguments
            additional_args = []
            if self.console_var.get():
                additional_args.append("--console")
            else:
                additional_args.append("--noconsole")

            # Start build
            result = self.builder.build(
                self.project_path_var.get(),
                self.output_format_var.get(),
                additional_args,
            )

            # Update UI in main thread
            self.root.after(0, lambda: self._build_finished(result))

        except Exception as e:
            logger.error(f"Error dalam build worker: {e}")
            self.root.after(0, lambda: self._build_finished(None))

    def _build_finished(self, result: Optional[BuildResult]):
        """Callback ketika build selesai."""
        # Re-enable build button, disable cancel button
        self.build_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        if result and result.success:
            self.progress_var.set(100)
            self.progress_label.config(text="Build selesai!")
            self.status_label.config(text="Build berhasil")

            messagebox.showinfo(
                "Sukses", f"Build selesai!\nOutput: {result.output_path}"
            )

            self._log_message(f"Build berhasil dalam {result.build_time:.2f} detik")
            self._log_message(f"Output: {result.output_path}")

        else:
            self.progress_var.set(0)
            self.progress_label.config(text="Build gagal")
            self.status_label.config(text="Build gagal")

            error_msg = result.error_message if result else "Error tidak diketahui"
            messagebox.showerror("Error", f"Build gagal: {error_msg}")

            self._log_message(f"Build gagal: {error_msg}")

    def _cancel_build(self):
        """Membatalkan build yang sedang berjalan."""
        if self.builder:
            if self.builder.cancel_build():
                self.progress_label.config(text="Build dibatalkan")
                self.status_label.config(text="Build dibatalkan")
                self._log_message("Build dibatalkan oleh user")
            else:
                messagebox.showwarning("Warning", "Tidak dapat membatalkan build")

    def _clear_log(self):
        """Membersihkan log."""
        self.log_text.delete(1.0, tk.END)

    def _save_log(self):
        """Menyimpan log ke file."""
        file_path = filedialog.asksaveasfilename(
            title="Simpan Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Sukses", f"Log disimpan ke: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan log: {e}")

    def _save_config(self):
        """Menyimpan konfigurasi."""
        config = {
            "last_project": self.project_path_var.get(),
            "output_format": self.output_format_var.get(),
        }
        self.config_manager.save_config(config)

    def _log_message(self, message: str):
        """Menambahkan pesan ke log queue."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def _process_log_queue(self):
        """Memproses log queue."""
        while True:
            try:
                message = self.log_queue.get(timeout=0.1)
                self.root.after(0, lambda msg=message: self._add_log_message(msg))
            except queue.Empty:
                continue

    def _add_log_message(self, message: str):
        """Menambahkan pesan ke log text area."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def run(self):
        """Menjalankan aplikasi."""
        self.root.mainloop()
