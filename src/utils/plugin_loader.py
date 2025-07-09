import importlib
import json
import os
from typing import Any

PLUGIN_PATH = os.path.join(os.path.dirname(__file__), "..", "plugins")


def get_available_plugins() -> list[str]:
    """
    Mengembalikan daftar nama plugin yang tersedia di folder plugins.
    """
    return [
        f[:-3]
        for f in os.listdir(PLUGIN_PATH)
        if f.endswith("_plugin.py") and not f.startswith("__")
    ]


def load_plugins(app: Any, active_plugins: list[str]):
    """
    Memuat dan mendaftarkan plugin yang aktif ke aplikasi.
    """
    for plugin_name in active_plugins:
        try:
            module = importlib.import_module(f"src.plugins.{plugin_name}")
            if hasattr(module, "register_plugin"):
                module.register_plugin(app)
        except Exception as e:
            print(f"Gagal memuat plugin {plugin_name}: {e}")


def unload_plugin(app: Any, plugin_name: str):
    """
    Membongkar (unregister) plugin dari aplikasi.
    """
    try:
        module = importlib.import_module(f"src.plugins.{plugin_name}")
        if hasattr(module, "unregister_plugin"):
            module.unregister_plugin(app)
    except Exception as e:
        print(f"Gagal membongkar plugin {plugin_name}: {e}")
