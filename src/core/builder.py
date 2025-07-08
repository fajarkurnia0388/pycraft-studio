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
from typing import List, Optional, Any

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
    status: 'BuildStatus'
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

        # Ensure output directory exists
        FileManager.ensure_directory_exists(self.output_directory)

    def build(
        self,
        python_file: str,
        output_format: str,
        additional_args: Optional[List[str]] = None,
    ) -> BuildResult:
        """
        Membangun proyek Python menjadi executable.

        Args:
            python_file: Path ke file Python yang akan di-build.
            output_format: Format output (exe, app, binary).
            additional_args: Argumen tambahan untuk PyInstaller.

        Returns:
            BuildResult berisi hasil build.
        """
        start_time = time.time()
        self.build_status = BuildStatus.RUNNING

        try:
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

            # Prepare build command
            cmd = self._prepare_build_command(
                python_file, output_format, additional_args
            )

            # Execute build
            result = self._execute_build(cmd, python_file)
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
        Membatalkan build yang sedang berjalan.

        Returns:
            True jika berhasil dibatalkan, False jika tidak.
        """
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                self.build_status = BuildStatus.CANCELLED
                logger.info("Build berhasil dibatalkan")
                return True
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                self.build_status = BuildStatus.CANCELLED
                logger.warning("Build dipaksa dibatalkan")
                return True
            except Exception as e:
                logger.error(f"Error saat membatalkan build: {e}")
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
            if not file_path.endswith('.py'):
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

        # Add output directory
        cmd.extend([f"--distpath={self.output_directory}"])

        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)

        # Add input file
        cmd.append(python_file)

        logger.info(f"Build command: {' '.join(cmd)}")
        return cmd

    def _execute_build(self, cmd: List[str], python_file: str) -> BuildResult:
        """
        Menjalankan proses build.

        Args:
            cmd: Command untuk dijalankan.
            python_file: Path ke file Python.

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

            # Capture output
            stdout, stderr = self.current_process.communicate()
            return_code = self.current_process.returncode

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

    def get_build_status(self) -> 'BuildStatus':
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
