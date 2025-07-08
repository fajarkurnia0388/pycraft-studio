"""
Tujuan: Unit tests untuk modul config
Dependensi: pytest, src.core.config
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.config import ConfigManager


class TestConfigManager:
    """Test cases untuk ConfigManager."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        # Create temporary directory for config
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_settings.json"
        self.config_manager = ConfigManager(self.config_path)

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        # Remove temporary directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_with_custom_path(self):
        """Test inisialisasi dengan custom path."""
        assert self.config_manager.config_path == self.config_path
        # Tidak perlu cek base_dir karena test memang boleh di luar base_dir

    def test_load_config_file_not_found(self):
        """Test load config ketika file tidak ada."""
        config = self.config_manager.load_config()
        assert isinstance(config, dict)
        assert "last_project" in config
        assert "output_format" in config

    def test_load_config_invalid_json(self):
        """Test load config dengan JSON tidak valid."""
        # Create invalid JSON file
        with open(self.config_path, "w") as f:
            f.write("invalid json content")

        config = self.config_manager.load_config()
        assert isinstance(config, dict)
        assert config == self.config_manager.default_config

    def test_save_and_load_config(self):
        """Test save dan load config."""
        test_config = {
            "last_project": "/test/path.py",
            "output_format": "exe",
            "auto_save": True,
        }

        # Save config
        result = self.config_manager.save_config(test_config)
        assert result is True

        # Load config
        loaded_config = self.config_manager.load_config()
        assert loaded_config["last_project"] == "/test/path.py"
        assert loaded_config["output_format"] == "exe"

    def test_update_config(self):
        """Test update single config item."""
        # Update config
        result = self.config_manager.update_config("last_project", "/new/path.py")
        assert result is True

        # Check if updated
        config = self.config_manager.load_config()
        assert config["last_project"] == "/new/path.py"

    def test_get_config(self):
        """Test get config value."""
        # Set config
        self.config_manager.update_config("last_project", "/test/path.py")

        # Get config
        value = self.config_manager.get_config("last_project")
        assert value == "/test/path.py"

        # Get non-existent config
        value = self.config_manager.get_config("non_existent", "default")
        assert value == "default"

    def test_validate_config(self):
        """Test config validation."""
        invalid_config = {
            "last_project": 123,  # Should be string
            "output_format": "invalid_format",
            "unknown_key": "value",
        }

        validated = self.config_manager._validate_config(invalid_config)

        # Should use default for invalid types
        assert isinstance(validated["last_project"], str)
        # output_format harus fallback ke default jika value tidak valid
        assert (
            validated["output_format"]
            == self.config_manager.default_config["output_format"]
        )

    def test_reset_to_default(self):
        """Test reset config ke default."""
        # Set custom config
        self.config_manager.update_config("last_project", "/custom/path.py")

        # Reset to default
        result = self.config_manager.reset_to_default()
        assert result is True

        # Check if reset
        config = self.config_manager.load_config()
        assert config["last_project"] == ""
