"""
Tujuan: Unit tests untuk modul builder
Dependensi: pytest, unittest.mock, src.core.builder
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.core.builder import (BuildFormat, BuildResult, BuildStatus,
                              ProjectBuilder)


class TestProjectBuilder:
    """Test cases untuk ProjectBuilder."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.builder = ProjectBuilder(self.temp_dir)

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test inisialisasi ProjectBuilder."""
        assert self.builder.output_directory == self.temp_dir
        assert self.builder.build_status == BuildStatus.PENDING
        assert self.builder.current_process is None

    def test_get_supported_formats(self):
        """Test mendapatkan format yang didukung."""
        formats = self.builder.get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        # Semua format harus valid
        for fmt in formats:
            assert fmt in ["exe", "app", "binary"]

    @patch("src.core.builder.subprocess.run")
    def test_check_pyinstaller_available(self, mock_run):
        """Test cek ketersediaan PyInstaller."""
        # Mock successful check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PyInstaller 5.0.0"

        result = self.builder._check_pyinstaller()
        assert result is True
        mock_run.assert_called_once()

    @patch("src.core.builder.subprocess.run")
    def test_check_pyinstaller_not_available(self, mock_run):
        """Test cek PyInstaller tidak tersedia."""
        # Mock failed check
        mock_run.side_effect = FileNotFoundError()

        result = self.builder._check_pyinstaller()
        assert result is False

    def test_validate_build_input_valid(self):
        """Test validasi input build yang valid."""
        # Create temporary Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        # Use binary format for Linux
        result = self.builder._validate_build_input(str(test_file), "binary")
        assert result is True

    def test_validate_build_input_invalid_file(self):
        """Test validasi input dengan file tidak valid."""
        result = self.builder._validate_build_input("/nonexistent/file.py", "exe")
        assert result is False

    def test_validate_build_input_invalid_format(self):
        """Test validasi input dengan format tidak valid."""
        # Create temporary Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        result = self.builder._validate_build_input(str(test_file), "invalid_format")
        assert result is False

    def test_prepare_build_command(self):
        """Test menyiapkan command build."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        cmd = self.builder._prepare_build_command(str(test_file), "exe")
        assert isinstance(cmd, list)
        assert "pyinstaller" in cmd[0]
        assert "--onefile" in cmd
        assert str(test_file) in cmd

    def test_prepare_build_command_with_additional_args(self):
        """Test menyiapkan command build dengan argumen tambahan."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        additional_args = ["--debug", "--strip"]
        cmd = self.builder._prepare_build_command(
            str(test_file), "exe", additional_args
        )

        assert "--debug" in cmd
        assert "--strip" in cmd

    @patch("src.core.builder.subprocess.Popen")
    def test_execute_build_success(self, mock_popen):
        """Test eksekusi build yang berhasil."""
        # Mock successful build
        mock_process = Mock()
        mock_process.communicate.return_value = ("stdout", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        cmd = ["pyinstaller", "--onefile", str(test_file)]
        result = self.builder._execute_build(cmd, str(test_file))

        assert result.success is True
        assert result.status == BuildStatus.SUCCESS
        assert result.error_message is None

    @patch("src.core.builder.subprocess.Popen")
    def test_execute_build_failure(self, mock_popen):
        """Test eksekusi build yang gagal."""
        # Mock failed build
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "Error: Build failed")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        cmd = ["pyinstaller", "--onefile", str(test_file)]
        result = self.builder._execute_build(cmd, str(test_file))

        assert result.success is False
        assert result.status == BuildStatus.FAILED
        assert "Error: Build failed" in result.error_message

    def test_get_output_path(self):
        """Test mendapatkan path output."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        output_path = self.builder._get_output_path(str(test_file))
        assert "test" in output_path
        assert self.temp_dir in output_path

    @patch("src.core.builder.subprocess.Popen")
    @patch("src.core.builder.subprocess.run")
    def test_build_integration_success(self, mock_run, mock_popen):
        """Test integrasi build yang berhasil."""
        # Mock PyInstaller check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PyInstaller 5.0.0"
        
        # Mock successful build
        mock_process = Mock()
        mock_process.communicate.return_value = ("stdout", "")
        mock_process.returncode = 0
        # Make the mock support context manager protocol
        mock_process.__enter__ = Mock(return_value=mock_process)
        mock_process.__exit__ = Mock(return_value=None)
        mock_popen.return_value = mock_process

        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        result = self.builder.build(str(test_file), "binary")

        assert result.success is True
        assert result.status == BuildStatus.SUCCESS
        assert result.build_time > 0

    @patch("src.core.builder.subprocess.Popen")
    @patch("src.core.builder.subprocess.run")
    def test_build_integration_failure(self, mock_run, mock_popen):
        """Test integrasi build yang gagal."""
        # Mock PyInstaller check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PyInstaller 5.0.0"
        
        # Mock failed build
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "Error: Build failed")
        mock_process.returncode = 1
        # Make the mock support context manager protocol
        mock_process.__enter__ = Mock(return_value=mock_process)
        mock_process.__exit__ = Mock(return_value=None)
        mock_popen.return_value = mock_process

        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        result = self.builder.build(str(test_file), "binary")

        assert result.success is False
        assert result.status == BuildStatus.FAILED
        assert result.error_message is not None
        assert "Error: Build failed" in result.error_message

    def test_cancel_build_no_process(self):
        """Test cancel build ketika tidak ada proses."""
        result = self.builder.cancel_build()
        assert result is False

    @patch("src.core.builder.subprocess.Popen")
    def test_cancel_build_with_process(self, mock_popen):
        """Test cancel build dengan proses yang sedang berjalan."""
        # Mock running process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = 0
        # Make the mock support context manager protocol
        mock_process.__enter__ = Mock(return_value=mock_process)
        mock_process.__exit__ = Mock(return_value=None)
        mock_popen.return_value = mock_process

        # Start a build to set current_process
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        # Mock the build to set current_process
        with patch.object(self.builder, "_check_pyinstaller", return_value=True):
            with patch.object(self.builder, "_validate_build_input", return_value=True):
                with patch.object(
                    self.builder, "_prepare_build_command", return_value=["test"]
                ):
                    with patch.object(self.builder, "_execute_build") as mock_execute:
                        mock_execute.return_value = BuildResult(
                            success=True,
                            output_path="test",
                            error_message=None,
                            build_time=1.0,
                            status=BuildStatus.SUCCESS,
                            log_output="",
                        )
                        self.builder.build(str(test_file), "exe")
        # Set current_process ke mock_process agar cancel_build bisa bekerja
        self.builder.current_process = mock_process

        # Now test cancel
        result = self.builder.cancel_build()
        assert result is True
        assert self.builder.build_status == BuildStatus.CANCELLED
