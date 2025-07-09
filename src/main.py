"""
Tujuan: Entry point utama aplikasi PyCraft Studio Enhanced.
Dependensi: src.gui.enhanced_main_window, src.core.config, logging, sys
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: python -m src.main
"""

import logging
import sys

from src.core.config import ConfigManager
from src.gui.enhanced_main_window import EnhancedMainWindow


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("builder_app.log"),  # Log ke file
            logging.StreamHandler(),  # Log ke console
        ],
    )
    return logging.getLogger(__name__)


def main():
    """Main function."""
    logger = setup_logging()
    try:
        logger.info("Memulai PyCraft Studio Enhanced")
        # Create and run enhanced main window
        app = EnhancedMainWindow()
        logger.info("Enhanced main window berhasil dibuat")
        app.run()
        logger.info("Aplikasi selesai")
        return 0
    except Exception as e:
        logger.error(f"Error saat menjalankan aplikasi: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
