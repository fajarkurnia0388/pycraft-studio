# PyCraft Studio - Enhanced

## 📚 Dokumentasi Lengkap

- [Quick Start](docs/QUICK_START.md)
- [Workflow Lengkap](docs/WORKFLOW.md)
- [Panduan Fitur & API](docs/DOCUMENTATION.md)
- [Panduan Installer](docs/installer_guide.md)
- [FAQ & Troubleshooting](docs/README_FAQ.md)
- [Changelog](CHANGELOG.md)
- [Progress Log](progress_log.md)

> Semua dokumentasi tambahan kini ada di folder `docs/` untuk kemudahan navigasi dan kerapian.

## Tentang PyCraft Studio

**PyCraft Studio** adalah aplikasi desktop berbasis Python yang dirancang untuk membantu developer membuat, mengelola, dan membangun proyek Python secara terstandarisasi agar dapat dengan mudah dikonversi menjadi aplikasi executable (.exe, .app, ELF) di berbagai sistem operasi (Windows, Linux, MacOS). Dengan fitur project templating, dependency analysis, validasi struktur, dan build system otomatis, PyCraft Studio memastikan setiap proyek Python yang dibuat sudah sesuai standar terbaik dan siap didistribusikan ke end-user tanpa repot.

Aplikasi GUI Python untuk membangun script Python menjadi executable dengan fitur project management, dependency analysis, dan validation yang canggih.

## 🚀 Fitur Utama

### 🔨 Build Executable
- Build script Python menjadi executable (.exe, .app, binary)
- Support multiple output formats berdasarkan OS
- Progress tracking dan logging real-time
- Cancel build process

### 📁 Project Templates
- Template untuk berbagai jenis aplikasi:
  - **Console Application** - Aplikasi command line dengan Click
  - **GUI Application** - Aplikasi GUI dengan tkinter
  - **Web Application** - Aplikasi web dengan Flask
  - **API Application** - API dengan FastAPI
- Struktur proyek standar otomatis
- File konfigurasi dan dokumentasi otomatis

### 🔍 Dependency Analysis
- Analisis dependencies otomatis dari import statements
- Deteksi dependencies yang hilang
- Validasi kompatibilitas dan security
- Generate requirements.txt otomatis
- Rekomendasi optimasi dependencies

### ✅ Project Validation
- Validasi struktur proyek sesuai best practices
- Validasi entry point dan konfigurasi
- Scoring dan rekomendasi perbaikan
- Auto-fix struktur proyek
- Laporan validasi lengkap

### 🛠️ Enhanced Build Process
- Build dengan validasi otomatis
- Optimasi build arguments berdasarkan dependencies
- Security scanning
- Performance optimization
- Comprehensive build reports

## 📋 Requirements

- Python 3.9+
- ttkbootstrap >=1.10.1
- PyInstaller 5.0.0+
- Dependencies lainnya lihat `requirements.txt`

## 🚀 Instalasi

1. **Clone repository**
```bash
git clone https://github.com/fajarkurnia0388/pycraft-studio.git
cd pycraft-studio
```

2. **(Opsional) Buat dan aktifkan virtual environment**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Jalankan aplikasi**
```bash
python -m src.main
```

## 🛠️ Troubleshooting Umum

- **PyInstaller not found:**
  ```bash
  pip install pyinstaller
  ```
- **File tidak valid:**
  ```bash
  python -m py_compile your_file.py
  ```
- **Dependencies missing:**
  ```bash
  pip install -r requirements.txt
  ```
- **Permission denied:**
  ```bash
  # Linux/Mac
  chmod +w output/
  # Windows: Run as Administrator
  ```

## 📖 Penggunaan

### 🚀 Quick Start
Lihat **[QUICK_START.md](QUICK_START.md)** untuk mulai dalam 5 menit!

### 📋 Workflow Lengkap
Lihat **[WORKFLOW.md](WORKFLOW.md)** untuk petunjuk penggunaan detail.

### 1. Build Executable
1. Buka tab "Build"
2. Pilih file Python yang akan di-build
3. Pilih format output (exe/app/binary)
4. Klik "Build" dan tunggu proses selesai

### 2. Buat Project Baru
1. Buka tab "Project Templates"
2. Masukkan nama proyek
3. Pilih template yang sesuai
4. Pilih lokasi output
5. Klik "Create Project"

### 3. Analisis Dependencies
1. Buka tab "Dependency Analysis"
2. Pilih path proyek
3. Klik "Analyze Project"
4. Lihat hasil analisis dan rekomendasi

### 4. Validasi Proyek
1. Buka tab "Project Validation"
2. Pilih path proyek
3. Klik "Validate Structure"
4. Ikuti rekomendasi perbaikan

## 🏗️ Struktur Proyek

```
PyCraft-Studio/
├── src/
│   ├── core/
│   │   ├── builder.py              # Core builder
│   │   ├── enhanced_builder.py     # Enhanced builder
│   │   ├── project_templates.py    # Project templates
│   │   ├── dependency_analyzer.py  # Dependency analysis
│   │   ├── build_validator.py      # Project validation
│   │   ├── batch_builder.py        # Batch processing
│   │   └── config.py               # Configuration
│   ├── gui/
│   │   ├── main_window.py          # Original GUI
│   │   └── enhanced_main_window.py # Enhanced GUI
│   └── utils/
│       └── file_utils.py           # File utilities
├── tests/                          # Unit tests
├── config/                         # Configuration files
├── output/                         # Build output
├── src/main.py                     # Main entry point
├── requirements.txt                # Dependencies
└── README.md                       # Documentation
```

## 🧪 Testing

```bash
# Run semua tests
pytest tests/

# Run dengan coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_builder.py
```

## 🔧 Konfigurasi

Aplikasi menggunakan file konfigurasi JSON di `config/settings.json`:

```json
{
    "default_output_dir": "output",
    "auto_validation": true,
    "build_timeout": 300,
    "max_file_size": 10485760
}
```

## 📊 Template Proyek

### Console Application
```python
import click

@click.command()
@click.option('--name', default='World', help='Nama untuk disapa')
def main(name):
    """Aplikasi console sederhana."""
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

### GUI Application
```python
import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("My App")
        # GUI components...

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

### Web Application
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def main():
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
```

### API Application
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Hello World"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```

## 🎯 Fitur Advanced

### Dependency Analysis
- **Import Detection**: Mendeteksi semua import statements
- **Dependency Mapping**: Memetakan dependencies internal/external
- **Version Analysis**: Analisis versi dependencies
- **Security Scanning**: Deteksi vulnerabilities
- **Compatibility Check**: Validasi kompatibilitas

### Project Validation
- **Structure Validation**: Validasi struktur direktori
- **Entry Point Validation**: Validasi main function
- **Best Practices Check**: Pengecekan coding standards
- **Auto-fix**: Perbaikan otomatis struktur proyek
- **Scoring System**: Sistem scoring untuk kualitas proyek

### Build Optimization
- **Smart Arguments**: Optimasi PyInstaller arguments
- **Dependency-based Optimization**: Optimasi berdasarkan dependencies
- **Size Optimization**: Optimasi ukuran executable
- **Performance Tuning**: Tuning performa build

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- PyInstaller untuk build system
- tkinter untuk GUI framework
- Python community untuk best practices

## 📞 Support

Jika ada pertanyaan atau masalah, silakan buat issue di repository ini.

---

**PyCraft Studio Enhanced** - Membuat executable Python menjadi lebih mudah dan profesional! 🐍✨ 