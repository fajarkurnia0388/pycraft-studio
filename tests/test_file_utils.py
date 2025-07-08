"""
Tujuan: Unit tests untuk modul file_utils
Dependensi: pytest, src.utils.file_utils
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.file_utils import FileManager, FileValidator


class TestFileValidator:
    """Test cases untuk FileValidator."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_valid_python_file_valid(self):
        """Test validasi file Python yang valid."""
        # Create valid Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        result = FileValidator.is_valid_python_file(str(test_file))
        assert result is True

    def test_is_valid_python_file_not_exists(self):
        """Test validasi file yang tidak ada."""
        result = FileValidator.is_valid_python_file("/nonexistent/file.py")
        assert result is False

    def test_is_valid_python_file_directory(self):
        """Test validasi direktori (bukan file)."""
        result = FileValidator.is_valid_python_file(self.temp_dir)
        assert result is False

    def test_is_valid_python_file_wrong_extension(self):
        """Test validasi file dengan ekstensi salah."""
        # Create file with wrong extension
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("print('Hello World')")

        result = FileValidator.is_valid_python_file(str(test_file))
        assert result is False

    def test_is_valid_python_file_dangerous_pattern(self):
        """Test validasi file dengan pola berbahaya."""
        result = FileValidator.is_valid_python_file("../../../etc/passwd")
        assert result is False

    def test_is_valid_python_file_too_large(self):
        """Test validasi file yang terlalu besar."""
        # Create large file (simulate)
        test_file = Path(self.temp_dir) / "large.py"
        # Write content that would make it large
        large_content = "print('x')" * 1000000  # Very large content
        test_file.write_text(large_content)

        result = FileValidator.is_valid_python_file(str(test_file))
        # Should fail due to size limit
        assert result is False

    def test_is_valid_python_file_syntax_error(self):
        """Test validasi file dengan syntax error."""
        # Create Python file with syntax error
        test_file = Path(self.temp_dir) / "syntax_error.py"
        test_file.write_text("print('Hello World'  # Missing closing parenthesis")

        result = FileValidator.is_valid_python_file(str(test_file))
        assert result is False

    def test_contains_dangerous_patterns(self):
        """Test deteksi pola berbahaya."""
        dangerous_paths = [
            "../../../etc/passwd",
            "//etc/passwd",
            "C:\\Windows\\System32\\cmd.exe",
        ]

        for path in dangerous_paths:
            assert FileValidator._contains_dangerous_patterns(path) is True

    def test_contains_dangerous_patterns_safe(self):
        """Test path yang aman."""
        safe_paths = [
            "/home/user/project/test.py",
            "C:/Users/username/project/test.py",
            "./test.py",
        ]

        for path in safe_paths:
            assert FileValidator._contains_dangerous_patterns(path) is False

    def test_sanitize_filename(self):
        """Test sanitasi nama file."""
        dangerous_names = [
            'file<>:"/\\|?*.txt',
            "file with spaces.txt",
            "file...txt",
            "",
        ]

        expected_safe_names = [
            "file_________.txt",
            "file with spaces.txt",
            "file...txt",
            "unnamed_file",
        ]

        for dangerous, expected in zip(dangerous_names, expected_safe_names):
            sanitized = FileValidator.sanitize_filename(dangerous)
            assert sanitized == expected


class TestFileManager:
    """Test cases untuk FileManager."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_directory_exists_new(self):
        """Test membuat direktori baru."""
        new_dir = Path(self.temp_dir) / "new_directory"

        result = FileManager.ensure_directory_exists(str(new_dir))
        assert result is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_exists_existing(self):
        """Test direktori yang sudah ada."""
        existing_dir = Path(self.temp_dir) / "existing_directory"
        existing_dir.mkdir()

        result = FileManager.ensure_directory_exists(str(existing_dir))
        assert result is True
        assert existing_dir.exists()

    def test_get_file_info_valid(self):
        """Test mendapatkan info file yang valid."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello World")

        info = FileManager.get_file_info(str(test_file))
        assert info is not None
        assert info["name"] == "test.txt"
        assert info["extension"] == ".txt"
        assert info["is_file"] is True
        assert info["is_directory"] is False
        assert info["size"] > 0

    def test_get_file_info_not_exists(self):
        """Test mendapatkan info file yang tidak ada."""
        info = FileManager.get_file_info("/nonexistent/file.txt")
        assert info is None

    def test_copy_file_safely_valid(self):
        """Test menyalin file dengan aman."""
        # Create source file
        source_file = Path(self.temp_dir) / "source.py"
        source_file.write_text("print('Hello World')")

        # Destination
        dest_file = Path(self.temp_dir) / "dest.py"

        result = FileManager.copy_file_safely(str(source_file), str(dest_file))
        assert result is True
        assert dest_file.exists()
        assert dest_file.read_text() == "print('Hello World')"

    def test_copy_file_safely_invalid_source(self):
        """Test menyalin file dengan source tidak valid."""
        dest_file = Path(self.temp_dir) / "dest.py"

        result = FileManager.copy_file_safely("/nonexistent/source.py", str(dest_file))
        assert result is False
        assert not dest_file.exists()

    def test_list_python_files(self):
        """Test mendapatkan daftar file Python."""
        # Create Python files
        python_files = [
            Path(self.temp_dir) / "test1.py",
            Path(self.temp_dir) / "test2.py",
            Path(self.temp_dir) / "subdir" / "test3.py",
        ]

        # Create subdirectory
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()

        # Write content to files
        for file in python_files:
            file.write_text("print('Hello World')")

        # Create non-Python file
        non_python = Path(self.temp_dir) / "test.txt"
        non_python.write_text("Not Python")

        files = FileManager.list_python_files(self.temp_dir)
        assert len(files) == 3
        assert all(file.endswith(".py") for file in files)

    def test_list_python_files_empty_directory(self):
        """Test mendapatkan daftar file Python di direktori kosong."""
        files = FileManager.list_python_files(self.temp_dir)
        assert files == []

    def test_list_python_files_invalid_directory(self):
        """Test mendapatkan daftar file Python di direktori tidak valid."""
        files = FileManager.list_python_files("/nonexistent/directory")
        assert files == []

    def test_get_relative_path_same_directory(self):
        """Test mendapatkan path relatif dalam direktori yang sama."""
        base_dir = Path(self.temp_dir)
        file_path = base_dir / "test.py"

        relative = FileManager.get_relative_path(str(file_path), str(base_dir))
        assert relative == "test.py"

    def test_get_relative_path_subdirectory(self):
        """Test mendapatkan path relatif dari subdirektori."""
        base_dir = Path(self.temp_dir)
        subdir = base_dir / "subdir"
        subdir.mkdir()
        file_path = subdir / "test.py"

        relative = FileManager.get_relative_path(str(file_path), str(base_dir))
        assert relative == "subdir/test.py"

    def test_get_relative_path_outside_base(self):
        """Test mendapatkan path relatif di luar base directory."""
        base_dir = Path(self.temp_dir)
        outside_file = Path("/tmp/outside.py")

        relative = FileManager.get_relative_path(str(outside_file), str(base_dir))
        assert relative == str(outside_file)
