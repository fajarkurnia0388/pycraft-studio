# Workflow dan Petunjuk Penggunaan PyCraft Studio Enhanced

## 📋 Daftar Isi
1. [Instalasi dan Setup](#instalasi-dan-setup)
2. [Workflow Dasar](#workflow-dasar)
3. [Workflow Project Management](#workflow-project-management)
4. [Workflow Build dengan Validasi](#workflow-build-dengan-validasi)
5. [Workflow Dependency Analysis](#workflow-dependency-analysis)
6. [Workflow Project Validation](#workflow-project-validation)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## 🚀 Instalasi dan Setup

### Prasyarat
- Python 3.8+
- Git
- Terminal/Command Prompt

### Langkah Instalasi

#### 1. Clone Repository
```bash
git clone <repository-url>
cd PyCraft-Studio
```

#### 2. Setup Virtual Environment (Recommended)
```bash
# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Verifikasi Instalasi
```bash
# Test aplikasi original
python main.py

# Test aplikasi enhanced
python main_enhanced.py
```

---

## 🔧 Workflow Dasar

### Scenario 1: Build Script Python Sederhana

#### Langkah-langkah:
1. **Buka Aplikasi**
   ```bash
   python main_enhanced.py
   ```

2. **Pilih Tab "Build"**

3. **Pilih File Python**
   - Klik "Browse"
   - Pilih file `.py` yang akan di-build
   - Pastikan file memiliki `if __name__ == "__main__":`

4. **Konfigurasi Build**
   - **Output Format**: Pilih sesuai OS target
     - `exe` - Windows executable
     - `app` - macOS application
     - `binary` - Linux binary
   - **Output Directory**: Pilih folder output

5. **Build**
   - Klik "Build"
   - Tunggu proses selesai
   - Cek hasil di folder output

#### Contoh File Python Sederhana:
```python
# hello.py
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

---

## 📁 Workflow Project Management

### Scenario 2: Buat Project Baru dari Template

#### Langkah-langkah:
1. **Buka Tab "Project Templates"**

2. **Isi Form Project**
   - **Project Name**: Nama proyek (contoh: `my_web_app`)
   - **Template**: Pilih jenis aplikasi
     - `console` - Aplikasi command line
     - `gui` - Aplikasi GUI dengan tkinter
     - `web` - Aplikasi web dengan Flask
     - `api` - API dengan FastAPI
   - **Output Path**: Lokasi penyimpanan proyek

3. **Review Template Info**
   - Lihat deskripsi template
   - Cek dependencies yang diperlukan
   - Review struktur file

4. **Create Project**
   - Klik "Create Project"
   - Tunggu proses selesai
   - Project siap digunakan

#### Struktur Project yang Dibuat:
```
my_web_app/
├── src/
│   ├── __init__.py
│   └── main.py          # Entry point
├── tests/
│   └── __init__.py
├── docs/
│   └── __init__.py
├── config/
│   └── __init__.py
├── resources/
│   └── __init__.py
├── requirements.txt     # Dependencies
├── README.md           # Dokumentasi
├── .gitignore          # Git ignore
└── build_config.py     # Build configuration
```

---

## 🔍 Workflow Dependency Analysis

### Scenario 3: Analisis Dependencies Project

#### Langkah-langkah:
1. **Buka Tab "Dependency Analysis"**

2. **Pilih Project Path**
   - Klik "Browse"
   - Pilih folder project yang akan dianalisis

3. **Jalankan Analisis**
   - Klik "Analyze Project"
   - Tunggu proses analisis selesai

4. **Review Hasil**
   - **Total Python Files**: Jumlah file Python
   - **External Dependencies**: Dependencies eksternal
   - **Standard Libraries**: Library standar Python
   - **Internal Modules**: Modul internal

5. **Generate Requirements**
   - Klik "Generate Requirements"
   - File `requirements.txt` akan dibuat otomatis

6. **Validate Dependencies**
   - Klik "Validate Dependencies"
   - Cek dependencies yang hilang

#### Contoh Output Analysis:
```
Total Python Files: 15

External Dependencies: 8
Standard Libraries: 12
Internal Modules: 3

Dependencies:
  - flask: 2.0.0
  - requests: latest
  - pandas: 1.3.0

Recommendations:
  - Pertimbangkan menambahkan pytest: Testing framework
  - Pertimbangkan menambahkan black: Code formatter
```

---

## ✅ Workflow Project Validation

### Scenario 4: Validasi Struktur Project

#### Langkah-langkah:
1. **Buka Tab "Project Validation"**

2. **Pilih Project Path**
   - Klik "Browse"
   - Pilih folder project yang akan divalidasi

3. **Jalankan Validasi**
   - Klik "Validate Structure"
   - Tunggu proses validasi selesai

4. **Review Hasil**
   - **Score**: Skor validasi (0-100%)
   - **Valid**: Status validasi (True/False)
   - **Errors**: Error yang ditemukan
   - **Warnings**: Peringatan
   - **Recommendations**: Rekomendasi perbaikan

5. **Generate Report**
   - Klik "Generate Report"
   - Laporan lengkap akan ditampilkan

6. **Fix Structure** (Jika diperlukan)
   - Klik "Fix Structure"
   - Struktur akan diperbaiki otomatis

#### Contoh Output Validation:
```
VALIDASI STRUKTUR PROYEK
========================
Path: /path/to/project
Status: VALID
Score: 92%

ERRORS:
✅ Tidak ada error

WARNINGS:
⚠️ File direkomendasikan tidak ditemukan: setup.py

RECOMMENDATIONS:
💡 Best practice: tambahkan src/__init__.py
💡 Best practice: tambahkan tests/__init__.py
```

---

## 🛠️ Workflow Build dengan Validasi

### Scenario 5: Build Project dengan Validasi Lengkap

#### Langkah-langkah:
1. **Persiapkan Project**
   - Pastikan project sudah divalidasi
   - Pastikan dependencies sudah terinstall

2. **Buka Tab "Build"**

3. **Pilih Entry Point**
   - Pilih file `src/main.py` atau `main.py`
   - Pastikan file valid

4. **Konfigurasi Build**
   - **Output Format**: Sesuai target OS
   - **Output Directory**: Folder output
   - **Auto Validation**: Aktifkan (recommended)

5. **Build dengan Validasi**
   - Klik "Build"
   - Sistem akan menjalankan:
     1. Validasi struktur project
     2. Analisis dependencies
     3. Validasi dependencies
     4. Optimasi build arguments
     5. Build executable

6. **Review Build Log**
   - Cek log build untuk informasi detail
   - Review validation report
   - Review dependency analysis

#### Contoh Build Log:
```
VALIDATION REPORT:
Path: /path/to/project
Status: VALID
Score: 92%

DEPENDENCY ANALYSIS:
Total Python Files: 15
External Dependencies: 8
Dependencies:
  - flask: 2.0.0
  - requests: latest

BUILD LOG:
PyInstaller tersedia: 6.14.1
Build command: pyinstaller --onefile --distpath=output --strip src/main.py
Build berhasil: output/app
```

---

## 🔧 Troubleshooting

### Error: PyInstaller not found
```bash
# Install PyInstaller
pip install pyinstaller

# Verifikasi instalasi
pyinstaller --version
```

### Error: File Python tidak valid
- Pastikan file memiliki syntax Python yang benar
- Cek apakah ada import yang tidak valid
- Pastikan file tidak kosong

### Error: Dependencies tidak lengkap
```bash
# Install dependencies yang hilang
pip install -r requirements.txt

# Atau install manual
pip install package_name
```

### Error: Permission denied
```bash
# Windows: Jalankan sebagai Administrator
# Linux/Mac: Cek permission folder
chmod +w output/
```

### Error: Build timeout
- Cek ukuran project
- Pastikan tidak ada infinite loop
- Cek dependencies yang berat

---

## 📚 Best Practices

### 1. Struktur Project
```
project_name/
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── core/            # Business logic
│   ├── utils/           # Utilities
│   └── config/          # Configuration
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── docs/
├── requirements.txt
├── README.md
└── .gitignore
```

### 2. Entry Point
```python
# src/main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function."""
    logger.info("Application started")
    # Your code here
    logger.info("Application finished")

if __name__ == "__main__":
    main()
```

### 3. Dependencies Management
- Gunakan virtual environment
- Pin versi dependencies di `requirements.txt`
- Update dependencies secara berkala
- Cek security vulnerabilities

### 4. Build Optimization
- Gunakan `--onefile` untuk distribusi
- Gunakan `--windowed` untuk GUI apps
- Exclude modules yang tidak diperlukan
- Optimasi ukuran dengan `--strip`

### 5. Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_builder.py
```

---

## 🎯 Tips dan Trik

### 1. Build untuk Multiple OS
```bash
# Windows
python main_enhanced.py  # Build .exe

# macOS
python main_enhanced.py  # Build .app

# Linux
python main_enhanced.py  # Build binary
```

### 2. Optimasi Ukuran Executable
- Gunakan `--exclude-module` untuk modul yang tidak diperlukan
- Gunakan `--strip` untuk mengurangi ukuran
- Hapus debug symbols

### 3. Debug Build Issues
- Cek log build untuk error detail
- Test file Python secara manual
- Cek dependencies compatibility

### 4. Automate Build Process
```bash
# Script untuk build otomatis
#!/bin/bash
python main_enhanced.py --auto-build --project-path ./my_project
```

---

## 📞 Support

### Dokumentasi
- README.md - Dokumentasi lengkap
- WORKFLOW.md - Petunjuk penggunaan
- progress_log.md - Log perkembangan

### Issues
- Buat issue di repository untuk bug report
- Sertakan log error dan steps to reproduce

### Contributing
- Fork repository
- Buat feature branch
- Submit pull request

---

**PyCraft Studio Enhanced** - Membuat executable Python menjadi lebih mudah dan profesional! 🐍✨ 