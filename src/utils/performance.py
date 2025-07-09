"""
Tujuan: Performance monitoring dan profiling untuk PyCraft Studio
Dependensi: time, cProfile, psutil, logging
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import cProfile
import io
import logging
import pstats
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import psutil

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor performa aplikasi secara real-time."""

    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
        self.process = psutil.Process()

    def get_system_info(self) -> Dict[str, Any]:
        """Mendapatkan informasi sistem."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "process_cpu": self.process.cpu_percent(),
                "process_memory": self.process.memory_info().rss / 1024 / 1024,  # MB
                "uptime": time.time() - self.start_time,
            }
        except Exception as e:
            logger.error(f"Error saat mendapatkan system info: {e}")
            return {}

    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performa operasi."""
        try:
            system_info = self.get_system_info()
            log_data = {
                "operation": operation,
                "duration": duration,
                "timestamp": time.time(),
                **system_info,
                **kwargs,
            }

            self.metrics[operation] = log_data
            logger.info(
                f"Performance: {operation} took {duration:.2f}s, "
                f"CPU: {system_info.get('cpu_percent', 0):.1f}%, "
                f"Memory: {system_info.get('process_memory', 0):.1f}MB"
            )

        except Exception as e:
            logger.error(f"Error saat logging performance: {e}")


class Profiler:
    """Profiler untuk analisis performa kode."""

    def __init__(self, output_file: Optional[str] = None):
        self.profiler = cProfile.Profile()
        self.output_file = output_file or "profile_results.prof"
        self.stats = None

    def start(self):
        """Mulai profiling."""
        self.profiler.enable()
        logger.info("Profiling started")

    def stop(self):
        """Stop profiling dan generate report."""
        self.profiler.disable()

        # Generate stats
        s = io.StringIO()
        self.stats = pstats.Stats(self.profiler, stream=s).sort_stats("cumulative")
        self.stats.print_stats(20)  # Top 20 functions

        # Save to file
        self.profiler.dump_stats(self.output_file)

        logger.info(f"Profiling completed. Results saved to {self.output_file}")
        logger.debug(f"Profile report:\n{s.getvalue()}")

        return s.getvalue()

    def get_top_functions(self, limit: int = 10) -> list:
        """Mendapatkan fungsi dengan waktu eksekusi tertinggi."""
        if not self.stats:
            return []

        try:
            # Get stats as string and parse manually
            s = io.StringIO()
            self.stats.print_stats(limit)
            stats_output = s.getvalue()

            # Simple parsing of stats output
            lines = stats_output.strip().split("\n")[3:]  # Skip header
            stats_list = []

            for line in lines:
                if line.strip() and "function" in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        stats_list.append(
                            {
                                "function": parts[5],
                                "calls": int(parts[0]),
                                "total_time": float(parts[1]),
                                "cumulative_time": float(parts[2]),
                            }
                        )

            return stats_list[:limit]

        except Exception as e:
            logger.error(f"Error saat mendapatkan top functions: {e}")
            return []


def performance_decorator(monitor: PerformanceMonitor):
    """Decorator untuk monitoring performa fungsi."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.log_performance(
                    operation=f"{func.__module__}.{func.__name__}",
                    duration=duration,
                    success=True,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.log_performance(
                    operation=f"{func.__module__}.{func.__name__}",
                    duration=duration,
                    success=False,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def profile_function(func: Callable) -> Callable:
    """Decorator untuk profiling fungsi."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = Profiler(f"profile_{func.__name__}.prof")
        profiler.start()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.stop()

    return wrapper


class BuildPerformanceTracker:
    """Tracker khusus untuk performa build process."""

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.build_times = []
        self.file_sizes = []

    def track_build(self, file_path: str, output_path: str, duration: float):
        """Track performa build."""
        try:
            # Get file sizes
            input_size = (
                Path(file_path).stat().st_size if Path(file_path).exists() else 0
            )
            output_size = (
                Path(output_path).stat().st_size if Path(output_path).exists() else 0
            )

            self.build_times.append(duration)
            self.file_sizes.append(
                {
                    "input": input_size,
                    "output": output_size,
                    "ratio": output_size / input_size if input_size > 0 else 0,
                }
            )

            self.monitor.log_performance(
                operation="build_process",
                duration=duration,
                input_size_mb=input_size / 1024 / 1024,
                output_size_mb=output_size / 1024 / 1024,
                compression_ratio=output_size / input_size if input_size > 0 else 0,
            )

        except Exception as e:
            logger.error(f"Error saat tracking build performance: {e}")

    def get_build_statistics(self) -> Dict[str, Any]:
        """Mendapatkan statistik build."""
        if not self.build_times:
            return {}

        return {
            "total_builds": len(self.build_times),
            "average_build_time": sum(self.build_times) / len(self.build_times),
            "fastest_build": min(self.build_times),
            "slowest_build": max(self.build_times),
            "average_compression_ratio": (
                sum(f["ratio"] for f in self.file_sizes) / len(self.file_sizes)
                if self.file_sizes
                else 0
            ),
        }


# Global instances
performance_monitor = PerformanceMonitor()
build_tracker = BuildPerformanceTracker()


def get_performance_summary() -> Dict[str, Any]:
    """Mendapatkan ringkasan performa aplikasi."""
    try:
        system_info = performance_monitor.get_system_info()
        build_stats = build_tracker.get_build_statistics()

        return {
            "system": system_info,
            "builds": build_stats,
            "uptime": system_info.get("uptime", 0),
        }
    except Exception as e:
        logger.error(f"Error saat mendapatkan performance summary: {e}")
        return {}
