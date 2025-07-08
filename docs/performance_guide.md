# Performance Monitoring & Profiling Guide

## Overview

PyCraft Studio dilengkapi dengan sistem performance monitoring dan profiling yang komprehensif untuk membantu developer mengoptimasi aplikasi mereka.

## Fitur Utama

### 1. Real-time Performance Monitoring

Sistem monitoring real-time yang melacak:
- CPU usage (sistem dan proses)
- Memory usage
- Disk usage
- Build time tracking
- File size analysis

### 2. Code Profiling

Profiling system menggunakan cProfile untuk:
- Identifikasi bottleneck
- Analisis waktu eksekusi fungsi
- Optimasi performa kode

### 3. Build Performance Tracking

Tracking khusus untuk build process:
- Build time per file
- Compression ratio analysis
- Performance trends

## Penggunaan

### Basic Performance Monitoring

```python
from src.utils.performance import performance_monitor, get_performance_summary

# Monitor operasi
performance_monitor.log_performance("build_operation", 2.5, success=True)

# Dapatkan ringkasan performa
summary = get_performance_summary()
print(f"CPU Usage: {summary['system']['cpu_percent']}%")
print(f"Memory Usage: {summary['system']['process_memory']:.1f}MB")
```

### Code Profiling

```python
from src.utils.performance import Profiler

# Profiling fungsi
profiler = Profiler("my_profile.prof")
profiler.start()

# Jalankan kode yang ingin di-profile
my_function()

# Stop profiling dan dapatkan report
report = profiler.stop()
print(report)

# Dapatkan top functions
top_functions = profiler.get_top_functions(10)
for func in top_functions:
    print(f"{func['function']}: {func['cumulative_time']:.3f}s")
```

### Performance Decorator

```python
from src.utils.performance import performance_decorator, performance_monitor

@performance_decorator(performance_monitor)
def my_function():
    # Kode yang akan di-monitor
    pass
```

### Build Performance Tracking

```python
from src.utils.performance import build_tracker

# Track build performance
build_tracker.track_build("input.py", "output.exe", 3.2)

# Dapatkan statistik
stats = build_tracker.get_build_statistics()
print(f"Average build time: {stats['average_build_time']:.2f}s")
print(f"Total builds: {stats['total_builds']}")
```

## Metrics yang Tersedia

### System Metrics
- `cpu_percent`: Persentase penggunaan CPU
- `memory_percent`: Persentase penggunaan memory
- `disk_usage`: Persentase penggunaan disk
- `process_cpu`: CPU usage proses aplikasi
- `process_memory`: Memory usage proses aplikasi (MB)
- `uptime`: Waktu aplikasi berjalan

### Build Metrics
- `total_builds`: Total jumlah build
- `average_build_time`: Rata-rata waktu build
- `fastest_build`: Waktu build tercepat
- `slowest_build`: Waktu build terlama
- `average_compression_ratio`: Rata-rata rasio kompresi

## Best Practices

### 1. Monitoring Strategy
- Monitor operasi kritis secara konsisten
- Set threshold untuk alert
- Analisis trend performa

### 2. Profiling Guidelines
- Profile di environment production-like
- Fokus pada bottleneck yang signifikan
- Bandingkan sebelum dan sesudah optimasi

### 3. Build Optimization
- Track build time untuk file besar
- Monitor compression ratio
- Analisis dependency impact

## Troubleshooting

### Common Issues

1. **High CPU Usage**
   - Check for infinite loops
   - Optimize algorithms
   - Use caching where appropriate

2. **Memory Leaks**
   - Monitor memory usage over time
   - Check for unclosed resources
   - Use memory profiling tools

3. **Slow Build Times**
   - Analyze dependency tree
   - Optimize import statements
   - Consider parallel processing

### Performance Tips

1. **Code Optimization**
   ```python
   # Use list comprehension instead of loops
   result = [x * 2 for x in data]  # Faster
   
   # Use sets for lookups
   if item in set_data:  # O(1) lookup
   ```

2. **Memory Management**
   ```python
   # Use generators for large datasets
   def process_large_file(filename):
       with open(filename) as f:
           for line in f:
               yield process_line(line)
   ```

3. **Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def expensive_calculation(x):
       # Expensive operation
       pass
   ```

## Integration dengan CI/CD

Performance monitoring dapat diintegrasikan dengan CI/CD pipeline:

```yaml
# .github/workflows/performance.yml
name: Performance Check
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Performance Tests
        run: |
          python -m pytest tests/test_performance.py
          python -c "from src.utils.performance import get_performance_summary; print(get_performance_summary())"
```

## Monitoring Dashboard

Untuk monitoring yang lebih advanced, pertimbangkan menggunakan:
- **Grafana**: Untuk visualisasi metrics
- **Prometheus**: Untuk time-series data
- **ELK Stack**: Untuk log analysis

## Kesimpulan

Performance monitoring dan profiling adalah tools penting untuk:
- Mengidentifikasi bottleneck
- Mengoptimasi performa aplikasi
- Memastikan user experience yang baik
- Mengurangi resource usage

Gunakan fitur-fitur ini secara konsisten untuk mempertahankan performa aplikasi yang optimal. 