"""
Tujuan: Logika utama untuk membangun proyek Python menjadi executable
Dependensi: subprocess, platform, os, pathlib
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: builder = ProjectBuilder().build("script.py", "exe")
"""

import logging
import os
import platform
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional
import shlex

from src.utils.file_utils import FileManager, FileValidator

logger = logging.getLogger(__name__)


class BuildFormat(Enum):
    """Enum untuk format build yang didukung."""

    EXE = "exe"
    APP = "app"
    BINARY = "binary"


class BuildStatus(Enum):
    """Enum untuk status build."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildResult:
    """Data class untuk hasil build."""

    success: bool
    output_path: Optional[str]
    error_message: Optional[str]
    build_time: float
    status: "BuildStatus"
    log_output: str


class ProjectBuilder:
    """
    Builder untuk proyek Python menjadi executable.

    Menangani proses build menggunakan PyInstaller dengan
    validasi, error handling, dan progress tracking.
    """

    def __init__(self, output_directory: Optional[str] = None) -> None:
        """
        Inisialisasi ProjectBuilder.

        Args:
            output_directory: Direktori output untuk hasil build.
        """
        self.output_directory = output_directory or "output"
        self.current_process: Optional[subprocess.Popen] = None
        self.build_status = BuildStatus.PENDING
        self._cancel_requested = False  # Flag cancel

        # Ensure output directory exists
        FileManager.ensure_directory_exists(self.output_directory)

    def build(
        self,
        python_file: str,
        output_format: str,
        additional_args: Optional[List[str]] = None,
        use_spec: bool = False,
        spec_file: Optional[str] = None,
        extra_hiddenimports: Optional[List[str]] = None,
        timeout: int = 600,  # Timeout global build (detik)
    ) -> BuildResult:
        """
        Membangun proyek Python menjadi executable.

        Args:
            python_file: Path ke file Python yang akan di-build.
            output_format: Format output (exe, app, binary).
            additional_args: Argumen tambahan untuk PyInstaller.
            use_spec: Jika True, build menggunakan file .spec.
            spec_file: Path ke file .spec jika digunakan.
            extra_hiddenimports: List hidden import tambahan untuk patch .spec.
            timeout: Timeout global build (detik).

        Returns:
            BuildResult berisi hasil build.
        """
        start_time = time.time()
        self.build_status = BuildStatus.RUNNING
        self._cancel_requested = False  # Flag cancel
        try:
            # Preflight check dependency native
            preflight_log = self._preflight_check_native(python_file, additional_args)
            if preflight_log.get("error"):
                logger.error(f"Preflight check gagal: {preflight_log['error']}")
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message=f"Preflight check gagal: {preflight_log['error']}",
                    build_time=time.time() - start_time,
                    status=BuildStatus.FAILED,
                    log_output=preflight_log.get("log", ""),
                )
            # Cek keberadaan file PIL/_tkinter_finder.py jika build GUI
            try:
                import site
                import os
                pil_path = None
                for sp in site.getsitepackages():
                    candidate = os.path.join(sp, 'PIL', '_tkinter_finder.py')
                    if os.path.exists(candidate):
                        pil_path = candidate
                        break
                if not pil_path:
                    logger.warning('File PIL/_tkinter_finder.py tidak ditemukan di site-packages. Jika build GUI Python gagal, cek versi Pillow.')
            except Exception as e:
                logger.warning(f'Gagal cek file PIL/_tkinter_finder.py: {e}')
            # Validate input
            if not self._validate_build_input(python_file, output_format):
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message="Input tidak valid",
                    build_time=time.time() - start_time,
                    status=BuildStatus.FAILED,
                    log_output="",
                )

            # Check PyInstaller availability
            if not self._check_pyinstaller():
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message="PyInstaller tidak ditemukan",
                    build_time=time.time() - start_time,
                    status=BuildStatus.FAILED,
                    log_output="",
                )

            if use_spec and spec_file:
                # Patch .spec file untuk hidden import/resource
                if extra_hiddenimports:
                    self._patch_spec_hiddenimports(spec_file, extra_hiddenimports)
                cmd = ["pyinstaller", spec_file]
                logger.info(f"Build command (spec): {' '.join(cmd)}")
            else:
                # Prepare build command (CLI)
                cmd = self._prepare_build_command(
                    python_file, output_format, additional_args
                )
                logger.info(f"Build command: {' '.join(cmd)}")

            # Cek dan backup file output jika sudah ada
            output_path = self._get_output_path(python_file)
            if os.path.exists(output_path):
                try:
                    import datetime
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"{output_path}.bak_{ts}"
                    os.rename(output_path, backup_path)
                    logger.warning(f"File output sudah ada, dibackup ke: {backup_path}")
                except Exception as e:
                    logger.error(f"Gagal backup file output lama: {e}")
                    return BuildResult(
                        success=False,
                        output_path=None,
                        error_message=f"Gagal backup file output lama: {e}",
                        build_time=time.time() - start_time,
                        status=BuildStatus.FAILED,
                        log_output="",
                    )

            # Execute build with timeout
            result = self._execute_build(cmd, python_file, timeout)
            # Gabungkan log preflight dengan log build
            if hasattr(result, "log_output") and result.log_output:
                result.log_output = (preflight_log.get("log", "") or "") + result.log_output
            result.build_time = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"Error tidak terduga saat build: {e}")
            self.build_status = BuildStatus.FAILED
            return BuildResult(
                success=False,
                output_path=None,
                error_message=str(e),
                build_time=time.time() - start_time,
                status=BuildStatus.FAILED,
                log_output="",
            )

    def cancel_build(self) -> bool:
        """
        Membatalkan proses build yang sedang berjalan.
        Returns:
            True jika proses berhasil dibatalkan, False jika tidak.
        """
        if self.current_process and self.current_process.poll() is None:
            self._cancel_requested = True
            try:
                self.current_process.kill()
                logger.info("Proses build berhasil dibatalkan.")
                return True
            except Exception as e:
                logger.error(f"Gagal membatalkan proses build: {e}")
                return False
        return False

    def _validate_build_input(self, file_path: str, output_format: str) -> bool:
        """
        Validasi input untuk build.

        Args:
            file_path: Path ke file Python.
            output_format: Format output.

        Returns:
            True jika valid, False jika tidak.
        """
        try:
            # Validasi file path
            if not file_path or not os.path.exists(file_path):
                logger.error(f"File tidak ditemukan: {file_path}")
                return False

            # Validasi ekstensi file
            if not file_path.endswith(".py"):
                logger.error(f"File harus ber ekstensi .py: {file_path}")
                return False

            # Validasi format output
            if output_format not in self.get_supported_formats():
                logger.error(f"Format output tidak didukung: {output_format}")
                return False

            # Validasi file Python menggunakan FileValidator
            if not FileValidator.is_valid_python_file(file_path):
                logger.error(f"File Python tidak valid: {file_path}")
                return False

            logger.info(f"Validasi input berhasil: {file_path} -> {output_format}")
            return True

        except Exception as e:
            logger.error(f"Error saat validasi input: {e}")
            return False

    def _check_pyinstaller(self) -> bool:
        """
        Mengecek apakah PyInstaller tersedia.

        Returns:
            True jika tersedia, False jika tidak.
        """
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info(f"PyInstaller tersedia: {result.stdout.strip()}")
                return True
            else:
                logger.error("PyInstaller tidak ditemukan")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("PyInstaller tidak ditemukan atau timeout")
            return False

    def _is_format_supported_on_os(self, output_format: str, os_name: str) -> bool:
        """
        Mengecek apakah format didukung di OS tertentu.

        Args:
            output_format: Format output.
            os_name: Nama OS.

        Returns:
            True jika didukung, False jika tidak.
        """
        support_matrix = {
            "exe": ["windows"],
            "app": ["darwin"],
            "binary": ["linux", "darwin"],
        }

        return (
            output_format in support_matrix and os_name in support_matrix[output_format]
        )

    def _prepare_build_command(
        self,
        python_file: str,
        output_format: str,
        additional_args: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Menyiapkan command untuk build.

        Args:
            python_file: Path ke file Python.
            output_format: Format output.
            additional_args: Argumen tambahan.

        Returns:
            List berisi command untuk subprocess.
        """
        # Base command
        cmd = ["pyinstaller", "--onefile"]

        # Add format-specific options
        if output_format == "exe":
            cmd.extend(["--noconsole"])
        elif output_format == "app":
            # Additional options for macOS app
            cmd.extend(["--windowed"])

        # Add output directory (NO quoting here)
        cmd.append(f"--distpath={self.output_directory}")

        # Add additional arguments (NO quoting here)
        if additional_args:
            for arg in additional_args:
                if arg.startswith("--add-data="):
                    # Pisahkan src:dst, masukkan apa adanya
                    val = arg[len("--add-data="):]
                    if ":" in val:
                        src, dst = val.split(":", 1)
                        cmd.append(f"--add-data={src}:{dst}")
                    else:
                        cmd.append(arg)
                elif arg.startswith("--icon="):
                    icon_path = arg[len("--icon=") :]
                    cmd.append(f"--icon={icon_path}")
                else:
                    cmd.append(arg)

        # Add input file (NO quoting here)
        cmd.append(python_file)

        # Untuk preview command di log, tampilkan dengan quoting agar user bisa copy-paste
        preview_cmd = ' '.join(shlex.quote(x) for x in cmd)
        logger.info(f"Build command: {preview_cmd}")
        return cmd

    def _execute_build(self, cmd: List[str], python_file: str, timeout: int = 600) -> BuildResult:
        """
        Menjalankan proses build dengan timeout dan cancel support.
        Args:
            cmd: Command untuk dijalankan.
            python_file: Path ke file Python.
            timeout: Timeout global build (detik).
        Returns:
            BuildResult berisi hasil build.
        """
        try:
            # Start build process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            self._cancel_requested = False
            try:
                stdout, stderr = self.current_process.communicate(timeout=timeout)
                return_code = self.current_process.returncode
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                stdout, stderr = self.current_process.communicate()
                self.build_status = BuildStatus.FAILED
                logger.error("Build timeout (otomatis dihentikan)")
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message="Build timeout (otomatis dihentikan)",
                    build_time=0,
                    status=BuildStatus.FAILED,
                    log_output=stdout + stderr,
                )
            if self._cancel_requested:
                self.current_process.kill()
                logger.warning("Build dibatalkan oleh user.")
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message="Build dibatalkan oleh user.",
                    build_time=0,
                    status=BuildStatus.FAILED,
                    log_output=stdout + stderr,
                )

            # Prepare log output
            log_output = stdout + stderr

            if return_code == 0:
                # Build successful
                output_path = self._get_output_path(python_file)
                self.build_status = BuildStatus.SUCCESS
                logger.info(f"Build berhasil: {output_path}")

                return BuildResult(
                    success=True,
                    output_path=output_path,
                    error_message=None,
                    build_time=0,  # Will be set by caller
                    status=BuildStatus.SUCCESS,
                    log_output=log_output,
                )
            else:
                # Build failed
                self.build_status = BuildStatus.FAILED
                error_msg = stderr.strip() or "Build gagal dengan return code: " + str(
                    return_code
                )
                logger.error(f"Build gagal: {error_msg}")

                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message=error_msg,
                    build_time=0,  # Will be set by caller
                    status=BuildStatus.FAILED,
                    log_output=log_output,
                )

        except subprocess.TimeoutExpired:
            self.build_status = BuildStatus.FAILED
            logger.error("Build timeout")
            return BuildResult(
                success=False,
                output_path=None,
                error_message="Build timeout",
                build_time=0,
                status=BuildStatus.FAILED,
                log_output="",
            )
        except Exception as e:
            self.build_status = BuildStatus.FAILED
            logger.error(f"Error saat menjalankan build: {e}")
            return BuildResult(
                success=False,
                output_path=None,
                error_message=str(e),
                build_time=0,
                status=BuildStatus.FAILED,
                log_output="",
            )

    def _get_output_path(self, python_file: str) -> str:
        """
        Mendapatkan path output berdasarkan file input.

        Args:
            python_file: Path ke file Python.

        Returns:
            Path ke file output.
        """
        file_name = Path(python_file).stem

        # Determine extension based on OS
        current_os = platform.system().lower()
        if current_os == "windows":
            extension = ".exe"
        elif current_os == "darwin":
            extension = ""  # .app is a directory
        else:
            extension = ""  # Linux binary has no extension

        output_path = os.path.join(self.output_directory, file_name + extension)

        # For macOS .app, it's a directory
        if current_os == "darwin" and not extension:
            output_path = os.path.join(self.output_directory, file_name + ".app")

        return output_path

    def get_build_status(self) -> "BuildStatus":
        """
        Mendapatkan status build saat ini.

        Returns:
            BuildStatus saat ini.
        """
        return self.build_status

    def get_supported_formats(self) -> List[str]:
        """
        Mendapatkan daftar format yang didukung di OS saat ini.

        Returns:
            List berisi format yang didukung.
        """
        current_os = platform.system().lower()
        supported_formats = []

        for format_enum in BuildFormat:
            if self._is_format_supported_on_os(format_enum.value, current_os):
                supported_formats.append(format_enum.value)

        return supported_formats

    def _patch_spec_hiddenimports(self, spec_file: str, hiddenimports: list):
        """Patch file .spec untuk menambah hiddenimports jika belum ada."""
        try:
            with open(spec_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if "hiddenimports=" in line:
                    # Tambahkan hidden import jika belum ada
                    for hi in hiddenimports:
                        if hi not in line:
                            line = line.rstrip().rstrip("]") + f", '{hi}']\n"
                new_lines.append(line)
            with open(spec_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            logger.info(f"Patched .spec file {spec_file} with hiddenimports: {hiddenimports}")
        except Exception as e:
            logger.warning(f"Gagal patch .spec file: {e}")

    def _preflight_check_native(self, python_file: str, additional_args: Optional[list]) -> dict:
        """
        Preflight check dependency native (tcl/tk, compiler, library OS).
        Returns dict: {"error": str, "log": str}
        """
        import shutil
        import sys
        import importlib.util
        log = []
        # Cek tcl/tk jika build GUI tkinter
        need_tk = False
        if additional_args:
            for arg in additional_args:
                if "tkinter" in arg or "ttkbootstrap" in arg or "--windowed" in arg:
                    need_tk = True
        if need_tk:
            try:
                import tkinter
                if not hasattr(tkinter, "Tk"):
                    raise ImportError("tkinter.Tk tidak ditemukan")
                log.append("[OK] Modul tkinter tersedia.")
            except Exception as e:
                return {"error": f"tkinter/tcl/tk tidak ditemukan: {e}", "log": "[ERROR] tkinter/tcl/tk tidak ditemukan\n"}
            # Cek tcl/tk library di OS
            if sys.platform.startswith("linux"):
                if not shutil.which("wish"):
                    log.append("[WARNING] Binary 'wish' (tcl/tk) tidak ditemukan di PATH. GUI mungkin gagal.")
            elif sys.platform == "darwin":
                if not shutil.which("wish"):
                    log.append("[WARNING] Binary 'wish' (tcl/tk) tidak ditemukan di PATH. GUI mungkin gagal.")
            elif sys.platform == "win32":
                # Windows biasanya bundle tcl/tk
                pass
        # Cek compiler (Linux/Mac)
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            if not shutil.which("gcc") and not shutil.which("clang"):
                log.append("[WARNING] Compiler C (gcc/clang) tidak ditemukan. Build ekstensi native mungkin gagal.")
        # Cek library OS penting (contoh: ldd di Linux)
        if sys.platform.startswith("linux"):
            if not shutil.which("ldd"):
                log.append("[WARNING] Tool 'ldd' tidak ditemukan. Tidak bisa cek dependency binary.")
        # Cek python3
        if not shutil.which("python3"):
            log.append("[WARNING] python3 tidak ditemukan di PATH.")
        # Cek PyInstaller
        if not shutil.which("pyinstaller"):
            return {"error": "PyInstaller tidak ditemukan di PATH.", "log": "[ERROR] PyInstaller tidak ditemukan\n"}
        # Cek importlib.metadata (untuk Python >=3.8)
        if importlib.util.find_spec("importlib.metadata") is None:
            log.append("[WARNING] importlib.metadata tidak tersedia. Validasi dependency terbatas.")
        return {"log": "[Preflight Check]\n" + "\n".join(log) + "\n"}
