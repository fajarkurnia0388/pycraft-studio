"""
Tujuan: Manajemen konfigurasi aplikasi PyCraft Studio
Dependensi: json, os
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: config = ConfigManager().load_config()
"""

import json
import logging
import os
from typing import Any, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manajer konfigurasi untuk aplikasi PyCraft Studio.

    Menangani penyimpanan dan pembacaan konfigurasi aplikasi
    dalam format JSON dengan validasi dan error handling.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inisialisasi ConfigManager.

        Args:
            config_path: Path ke file konfigurasi. Jika None,
                        akan menggunakan default path.
        """
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        if config_path is None:
            self.config_path = os.path.join(self.base_dir, "config", "settings.json")
        else:
            self.config_path = config_path

        # Default configuration
        self.default_config = {
            "last_project": "",
            "output_format": "exe",
            "auto_save": True,
            "output_directory": os.path.join(self.base_dir, "output"),
            "log_level": "INFO",
            "theme": "default",
            "custom_themes": {},
            "default_theme_overrides": {},
        }

        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """
        Load konfigurasi dari file.

        Returns:
            Dictionary berisi konfigurasi.
        """
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"File konfigurasi tidak ditemukan: {self.config_path}")
                return self.default_config.copy()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validasi konfigurasi
            validated_config = self._validate_config(config)
            logger.info(f"Konfigurasi berhasil dimuat dari: {self.config_path}")
            return validated_config
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON konfigurasi: {e}")
            logger.info("Menggunakan konfigurasi default")
            return self.default_config.copy()
        except Exception as e:
            logger.error(f"Error saat memuat konfigurasi: {e}")
            logger.info("Menggunakan konfigurasi default")
            return self.default_config.copy()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save konfigurasi ke file.

        Args:
            config: Dictionary berisi konfigurasi.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            # Validasi konfigurasi
            validated_config = self._validate_config(config)

            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, indent=2, ensure_ascii=False)

            logger.info(f"Konfigurasi berhasil disimpan ke: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saat menyimpan konfigurasi: {e}")
            return False

    def update_config(self, key: str, value: Any) -> bool:
        """
        Update single config item.

        Args:
            key: Kunci konfigurasi.
            value: Nilai baru.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            config = self.load_config()
            config[key] = value
            
            success = self.save_config(config)
            if success:
                logger.info(f"Konfigurasi '{key}' berhasil diupdate")
            return success
            
        except Exception as e:
            logger.error(f"Error saat update konfigurasi '{key}': {e}")
            return False

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get config value.

        Args:
            key: Kunci konfigurasi.
            default: Nilai default jika key tidak ditemukan.

        Returns:
            Nilai konfigurasi atau default.
        """
        try:
            config = self.load_config()
            value = config.get(key, default)
            logger.debug(f"Mengambil konfigurasi '{key}': {value}")
            return value
            
        except Exception as e:
            logger.error(f"Error saat mengambil konfigurasi '{key}': {e}")
            return default

    def get_custom_themes(self) -> Dict[str, Any]:
        config = self.load_config()
        return config.get("custom_themes", {})

    def set_custom_themes(self, custom_themes: Dict[str, Any]) -> bool:
        config = self.load_config()
        config["custom_themes"] = custom_themes
        return self.save_config(config)

    def get_default_theme_overrides(self) -> Dict[str, Any]:
        config = self.load_config()
        return config.get("default_theme_overrides", {})

    def set_default_theme_overrides(self, overrides: Dict[str, Any]) -> bool:
        config = self.load_config()
        config["default_theme_overrides"] = overrides
        return self.save_config(config)

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Memvalidasi konfigurasi dan menambahkan nilai default jika diperlukan.

        Args:
            config: Konfigurasi yang akan divalidasi.

        Returns:
            Konfigurasi yang sudah divalidasi.
        """
        validated_config = self.default_config.copy()

        for key, value in config.items():
            if key in self.default_config:
                expected_type = type(self.default_config[key])
                if key == "output_format":
                    if isinstance(value, expected_type) and value in [
                        "exe",
                        "app",
                        "binary",
                    ]:
                        validated_config[key] = value
                    else:
                        logger.warning(
                            f"Nilai output_format tidak valid: {value}. Menggunakan default."
                        )
                elif key == "custom_themes":
                    if isinstance(value, dict):
                        validated_config[key] = value
                    else:
                        logger.warning(f"custom_themes harus dict. Menggunakan default.")
                elif key == "default_theme_overrides":
                    if isinstance(value, dict):
                        validated_config[key] = value
                    else:
                        logger.warning(f"default_theme_overrides harus dict. Menggunakan default.")
                elif isinstance(value, expected_type):
                    validated_config[key] = value
                else:
                    logger.warning(
                        f"Tipe data tidak valid untuk {key}: {type(value)}. "
                        "Menggunakan default."
                    )
            else:
                logger.warning(f"Kunci konfigurasi tidak dikenal: {key}")

        return validated_config

    def reset_to_default(self) -> bool:
        """
        Reset konfigurasi ke nilai default.

        Returns:
            True jika berhasil direset, False jika gagal.
        """
        return self.save_config(self.default_config.copy())
