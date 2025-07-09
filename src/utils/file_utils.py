"""
Tujuan: Utilitas untuk operasi file dan validasi path
Dependensi: os, pathlib, re
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: is_valid_python_file("script.py")
"""

import logging
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileValidator:
    """
    Validator untuk operasi file dan path.

    Menyediakan fungsi validasi untuk keamanan dan integritas file.
    """

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".py", ".pyw"}

    # Dangerous patterns to avoid
    DANGEROUS_PATTERNS = [
        r"\.\./",  # Path traversal
        r"//",  # Multiple slashes
        r"\\",  # Backslashes (potential escape)
    ]

    @staticmethod
    def is_valid_python_file(file_path: str) -> bool:
        """
        Validasi file Python.

        Args:
            file_path: Path ke file.

        Returns:
            True jika valid, False jika tidak.
        """
        try:
            # Validasi path
            if not file_path or not os.path.exists(file_path):
                logger.error(f"File tidak ditemukan: {file_path}")
                return False

            # Validasi ekstensi
            if not file_path.endswith(".py"):
                logger.error(f"File harus ber ekstensi .py: {file_path}")
                return False

            # Validasi path berbahaya
            if FileValidator._contains_dangerous_patterns(file_path):
                logger.error(f"Path berbahaya terdeteksi: {file_path}")
                return False

            # Validasi ukuran file (max 10MB)
            file_size = os.path.getsize(file_path)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                logger.error(f"File terlalu besar ({file_size} bytes): {file_path}")
                return False

            # Validasi syntax Python
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    compile(content, file_path, "exec")
                logger.debug(f"File Python valid: {file_path}")
                return True
            except SyntaxError as e:
                logger.error(f"Syntax error di file {file_path}: {e}")
                return False
            except UnicodeDecodeError as e:
                logger.error(f"Encoding error di file {file_path}: {e}")
                return False

        except Exception as e:
            logger.error(f"Error saat validasi file {file_path}: {e}")
            return False

    @staticmethod
    def _contains_dangerous_patterns(path: str) -> bool:
        """
        Mengecek apakah path mengandung pola berbahaya.

        Args:
            path: Path yang akan dicek.

        Returns:
            True jika mengandung pola berbahaya, False jika tidak.
        """
        for pattern in FileValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, path):
                return True
        return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Membersihkan nama file dari karakter berbahaya.

        Args:
            filename: Nama file yang akan dibersihkan.

        Returns:
            Nama file yang sudah dibersihkan.
        """
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(". ")

        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed_file"

        return sanitized


class FileManager:
    """
    Manager untuk operasi file dan direktori.

    Menyediakan fungsi untuk operasi file yang aman dan terstruktur.
    """

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Memastikan direktori ada.

        Args:
            directory_path: Path direktori.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            if not directory_path:
                logger.error("Path direktori kosong")
                return False

            if os.path.exists(directory_path):
                if os.path.isdir(directory_path):
                    logger.debug(f"Direktori sudah ada: {directory_path}")
                    return True
                else:
                    logger.error(
                        f"Path sudah ada tapi bukan direktori: {directory_path}"
                    )
                    return False

            os.makedirs(directory_path, exist_ok=True)
            logger.info(f"Direktori berhasil dibuat: {directory_path}")
            return True

        except Exception as e:
            logger.error(f"Error saat membuat direktori {directory_path}: {e}")
            return False

    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        Mendapatkan informasi file.

        Args:
            file_path: Path ke file.

        Returns:
            Dictionary berisi informasi file atau None jika error.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": path.suffix,
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
            }
        except Exception as e:
            logger.error(f"Error saat mendapatkan info file: {e}")
            return None

    @staticmethod
    def copy_file_safely(source_path: str, dest_path: str) -> bool:
        """
        Menyalin file dengan aman.

        Args:
            source_path: Path file sumber.
            dest_path: Path file tujuan.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            # Validasi source file
            if not FileValidator.is_valid_python_file(source_path):
                logger.error(f"Source file tidak valid: {source_path}")
                return False

            # Validasi destination path
            dest_dir = os.path.dirname(dest_path)
            if dest_dir and not FileManager.ensure_directory_exists(dest_dir):
                logger.error(f"Gagal membuat direktori tujuan: {dest_dir}")
                return False

            # Copy file
            shutil.copy2(source_path, dest_path)
            logger.info(f"File berhasil disalin: {source_path} -> {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error saat menyalin file {source_path} -> {dest_path}: {e}")
            return False

    @staticmethod
    def list_python_files(directory: str) -> List[str]:
        """
        Mendapatkan daftar file Python dalam direktori.

        Args:
            directory: Path ke direktori.

        Returns:
            List berisi path file Python yang valid.
        """
        python_files = []

        try:
            dir_path = Path(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                logger.warning(f"Direktori tidak valid: {directory}")
                return python_files

            for file_path in dir_path.rglob("*.py"):
                if FileValidator.is_valid_python_file(str(file_path)):
                    python_files.append(str(file_path))

            logger.info(f"Ditemukan {len(python_files)} file Python di {directory}")
            return python_files

        except Exception as e:
            logger.error(f"Error saat mencari file Python: {e}")
            return python_files

    @staticmethod
    def get_relative_path(file_path: str, base_directory: str) -> str:
        """
        Mendapatkan path relatif dari file terhadap direktori dasar.

        Args:
            file_path: Path absolut ke file.
            base_directory: Direktori dasar untuk perhitungan relatif.

        Returns:
            Path relatif dari file.
        """
        try:
            file_path_obj = Path(file_path).resolve()
            base_path_obj = Path(base_directory).resolve()

            return str(file_path_obj.relative_to(base_path_obj))
        except ValueError:
            # File tidak dalam base directory
            return file_path
        except Exception as e:
            logger.error(f"Error saat menghitung path relatif: {e}")
            return file_path
