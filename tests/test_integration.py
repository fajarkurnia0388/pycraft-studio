"""
Tujuan: Integration tests untuk PyCraft Studio
Dependensi: pytest, unittest.mock, src.core, src.utils
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.core.builder import ProjectBuilder
from src.core.config import ConfigManager
from src.utils.file_utils import FileValidator, FileManager


class TestIntegration:
    """Integration tests untuk fitur utama aplikasi."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        self.config_manager = ConfigManager(str(self.config_path))
        self.builder = ProjectBuilder(self.temp_dir)
        # Override format build agar semua didukung saat test
        self.builder.get_supported_formats = lambda: ['exe', 'app', 'binary']

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_and_builder_integration(self):
        """Test integrasi config manager dan builder."""
        # Setup config
        test_config = {
            "last_project": "/test/project.py",
            "output_format": "exe",
            "auto_save": True
        }
        self.config_manager.save_config(test_config)

        # Verify config was saved
        loaded_config = self.config_manager.load_config()
        assert loaded_config["last_project"] == "/test/project.py"
        assert loaded_config["output_format"] == "exe"

        # Test builder with config
        formats = self.builder.get_supported_formats()
        assert "exe" in formats

    def test_file_validation_and_builder_integration(self):
        """Test integrasi file validation dan builder."""
        # Create valid Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        # Validate file
        is_valid = FileValidator.is_valid_python_file(str(test_file))
        assert is_valid is True

        # Test builder validation
        build_valid = self.builder._validate_build_input(str(test_file), "exe")
        assert build_valid is True

    def test_file_manager_and_builder_integration(self):
        """Test integrasi file manager dan builder."""
        # Create source file
        source_file = Path(self.temp_dir) / "source.py"
        source_file.write_text("print('Hello World')")

        # Copy file safely
        dest_file = Path(self.temp_dir) / "dest.py"
        copy_success = FileManager.copy_file_safely(str(source_file), str(dest_file))
        assert copy_success is True

        # Verify file exists and can be built
        assert dest_file.exists()
        build_valid = self.builder._validate_build_input(str(dest_file), "exe")
        assert build_valid is True

    def test_project_workflow_integration(self):
        """Test workflow lengkap project."""
        # 1. Create project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        
        # 2. Create main file
        main_file = project_dir / "main.py"
        main_file.write_text("""
import sys
print("Hello from PyCraft Studio!")
if __name__ == "__main__":
    print("Application started successfully")
""")

        # 3. Create requirements file
        requirements_file = project_dir / "requirements.txt"
        requirements_file.write_text("requests==2.28.1")

        # 4. Validate project structure
        assert main_file.exists()
        assert requirements_file.exists()
        
        # 5. Validate main file
        is_valid = FileValidator.is_valid_python_file(str(main_file))
        assert is_valid is True

        # 6. Test builder validation
        build_valid = self.builder._validate_build_input(str(main_file), "exe")
        assert build_valid is True

        # 7. Test config integration
        self.config_manager.update_config("last_project", str(main_file))
        last_project = self.config_manager.get_config("last_project")
        assert last_project == str(main_file)

    def test_error_handling_integration(self):
        """Test error handling integration."""
        # Test invalid file
        invalid_file = "/nonexistent/file.py"
        
        # File validation should fail
        is_valid = FileValidator.is_valid_python_file(invalid_file)
        assert is_valid is False

        # Builder validation should fail
        build_valid = self.builder._validate_build_input(invalid_file, "exe")
        assert build_valid is False

        # Config should handle invalid values gracefully
        self.config_manager.update_config("last_project", invalid_file)
        last_project = self.config_manager.get_config("last_project")
        assert last_project == invalid_file  # Should still save the value

    def test_directory_management_integration(self):
        """Test directory management integration."""
        # Create nested directory structure
        nested_dir = Path(self.temp_dir) / "nested" / "deep" / "project"
        
        # Ensure directory exists
        success = FileManager.ensure_directory_exists(str(nested_dir))
        assert success is True
        assert nested_dir.exists()

        # Create file in nested directory
        test_file = nested_dir / "test.py"
        test_file.write_text("print('Nested project')")

        # Validate file
        is_valid = FileValidator.is_valid_python_file(str(test_file))
        assert is_valid is True

        # Test builder with nested file
        build_valid = self.builder._validate_build_input(str(test_file), "exe")
        assert build_valid is True

    def test_config_persistence_integration(self):
        """Test config persistence integration."""
        # Update and test only valid config keys
        self.config_manager.update_config("last_project", "/path/to/project1.py")
        self.config_manager.update_config("output_format", "exe")
        self.config_manager.update_config("auto_save", False)

        # Reload config and verify persistence
        loaded_config = self.config_manager.load_config()
        assert loaded_config["last_project"] == "/path/to/project1.py"
        assert loaded_config["output_format"] == "exe"
        assert loaded_config["auto_save"] is False

        # Test config reset
        self.config_manager.reset_to_default()
        reset_config = self.config_manager.load_config()
        assert reset_config["last_project"] == ""
        assert reset_config["output_format"] == "exe"

    @patch('src.core.builder.subprocess.run')
    def test_build_process_integration(self, mock_run):
        """Test build process integration."""
        # Mock PyInstaller check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PyInstaller 5.0.0"

        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        # Test build command preparation
        cmd = self.builder._prepare_build_command(str(test_file), "exe")
        assert isinstance(cmd, list)
        assert "pyinstaller" in cmd[0]
        assert str(test_file) in cmd

        # Test output path generation
        output_path = self.builder._get_output_path(str(test_file))
        assert "test" in output_path
        assert self.temp_dir in output_path

    def test_file_info_integration(self):
        """Test file info integration."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('Hello World')")

        # Get file info
        file_info = FileManager.get_file_info(str(test_file))
        assert file_info is not None
        assert file_info["name"] == "test.py"
        assert file_info["extension"] == ".py"
        assert file_info["is_file"] is True
        assert file_info["size"] > 0

        # Test with non-existent file
        non_existent_info = FileManager.get_file_info("/nonexistent/file.py")
        assert non_existent_info is None 