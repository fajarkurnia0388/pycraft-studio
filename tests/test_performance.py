"""
Tujuan: Unit test untuk performance monitoring dan profiling
Dependensi: pytest, time, unittest.mock
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.performance import (
    PerformanceMonitor, 
    Profiler, 
    BuildPerformanceTracker,
    performance_decorator,
    get_performance_summary
)


class TestPerformanceMonitor:
    """Test untuk PerformanceMonitor."""
    
    def test_init(self):
        """Test inisialisasi PerformanceMonitor."""
        monitor = PerformanceMonitor()
        assert monitor.metrics == {}
        assert monitor.start_time > 0
        assert monitor.process is not None
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_info(self, mock_disk, mock_memory, mock_cpu):
        """Test mendapatkan informasi sistem."""
        # Mock return values
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 60.0
        mock_disk.return_value.percent = 45.0
        
        monitor = PerformanceMonitor()
        info = monitor.get_system_info()
        
        assert "cpu_percent" in info
        assert "memory_percent" in info
        assert "disk_usage" in info
        assert "process_cpu" in info
        assert "process_memory" in info
        assert "uptime" in info
    
    def test_log_performance(self):
        """Test logging performa."""
        monitor = PerformanceMonitor()
        
        with patch.object(monitor, 'get_system_info') as mock_info:
            mock_info.return_value = {"cpu_percent": 10.0, "process_memory": 50.0}
            
            monitor.log_performance("test_operation", 1.5, success=True)
            
            assert "test_operation" in monitor.metrics
            assert monitor.metrics["test_operation"]["duration"] == 1.5
            assert monitor.metrics["test_operation"]["success"] is True


class TestProfiler:
    """Test untuk Profiler."""
    
    def test_init(self):
        """Test inisialisasi Profiler."""
        profiler = Profiler()
        assert profiler.output_file == "profile_results.prof"
        assert profiler.stats is None
        
        profiler = Profiler("custom.prof")
        assert profiler.output_file == "custom.prof"
    
    def test_start_stop(self):
        """Test start dan stop profiling."""
        profiler = Profiler()
        
        profiler.start()
        # Simulate some work
        time.sleep(0.1)
        result = profiler.stop()
        
        assert result is not None
        assert "function calls" in result
        assert Path("profile_results.prof").exists()
        
        # Cleanup
        Path("profile_results.prof").unlink(missing_ok=True)
    
    def test_get_top_functions(self):
        """Test mendapatkan top functions."""
        profiler = Profiler()
        
        # Without stats, should return empty list
        assert profiler.get_top_functions() == []
        
        # With stats
        profiler.start()
        time.sleep(0.1)
        profiler.stop()
        
        # Should have some functions
        top_functions = profiler.get_top_functions(5)
        assert isinstance(top_functions, list)
        
        # Cleanup
        Path("profile_results.prof").unlink(missing_ok=True)


class TestBuildPerformanceTracker:
    """Test untuk BuildPerformanceTracker."""
    
    def test_init(self):
        """Test inisialisasi BuildPerformanceTracker."""
        tracker = BuildPerformanceTracker()
        assert tracker.build_times == []
        assert tracker.file_sizes == []
        assert tracker.monitor is not None
    
    @patch('pathlib.Path.stat')
    def test_track_build(self, mock_stat):
        """Test tracking build performance."""
        # Mock file stats
        mock_stat.return_value.st_size = 1024 * 1024  # 1MB
        
        tracker = BuildPerformanceTracker()
        
        with patch.object(tracker.monitor, 'log_performance') as mock_log:
            tracker.track_build("input.py", "output.exe", 2.5)
            
            assert len(tracker.build_times) == 1
            assert tracker.build_times[0] == 2.5
            assert len(tracker.file_sizes) == 1
            assert tracker.file_sizes[0]["input"] == 1024 * 1024
            assert tracker.file_sizes[0]["output"] == 1024 * 1024
            assert tracker.file_sizes[0]["ratio"] == 1.0
            
            mock_log.assert_called_once()
    
    def test_get_build_statistics(self):
        """Test mendapatkan statistik build."""
        tracker = BuildPerformanceTracker()
        
        # Empty stats
        stats = tracker.get_build_statistics()
        assert stats == {}
        
        # With data
        tracker.build_times = [1.0, 2.0, 3.0]
        tracker.file_sizes = [
            {"ratio": 0.8},
            {"ratio": 0.9},
            {"ratio": 1.0}
        ]
        
        stats = tracker.get_build_statistics()
        assert stats["total_builds"] == 3
        assert stats["average_build_time"] == 2.0
        assert stats["fastest_build"] == 1.0
        assert stats["slowest_build"] == 3.0
        assert abs(stats["average_compression_ratio"] - 0.9) < 0.01


class TestPerformanceDecorator:
    """Test untuk performance decorator."""
    
    def test_performance_decorator(self):
        """Test performance decorator."""
        monitor = PerformanceMonitor()
        
        @performance_decorator(monitor)
        def test_function():
            time.sleep(0.1)
            return "success"
        
        with patch.object(monitor, 'log_performance') as mock_log:
            result = test_function()
            
            assert result == "success"
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[1]["operation"] == "tests.test_performance.test_function"
            assert call_args[1]["success"] is True
    
    def test_performance_decorator_with_error(self):
        """Test performance decorator dengan error."""
        monitor = PerformanceMonitor()
        
        @performance_decorator(monitor)
        def test_function_with_error():
            time.sleep(0.1)
            raise ValueError("Test error")
        
        with patch.object(monitor, 'log_performance') as mock_log:
            with pytest.raises(ValueError):
                test_function_with_error()
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[1]["success"] is False
            assert call_args[1]["error"] == "Test error"


class TestPerformanceSummary:
    """Test untuk performance summary."""
    
    @patch('src.utils.performance.performance_monitor.get_system_info')
    @patch('src.utils.performance.build_tracker.get_build_statistics')
    def test_get_performance_summary(self, mock_build_stats, mock_system_info):
        """Test mendapatkan performance summary."""
        mock_system_info.return_value = {"cpu_percent": 25.0, "uptime": 100.0}
        mock_build_stats.return_value = {"total_builds": 5}
        
        summary = get_performance_summary()
        
        assert "system" in summary
        assert "builds" in summary
        assert "uptime" in summary
        assert summary["system"]["cpu_percent"] == 25.0
        assert summary["builds"]["total_builds"] == 5


if __name__ == "__main__":
    pytest.main([__file__]) 