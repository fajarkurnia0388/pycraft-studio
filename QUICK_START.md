# Quick Start Guide - PyCraft Studio Enhanced

## 🚀 Mulai dalam 5 Menit

### 1. Install & Setup (2 menit)
```bash
# Clone repository
git clone <repository-url>
cd PyCraft-Studio

# Install dependencies
pip install -r requirements.txt

# Run aplikasi
python main_enhanced.py
```

### 2. Build Script Pertama (3 menit)

#### Buat file Python sederhana:
```python
# hello.py
def main():
    print("Hello, PyCraft Studio!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
```

#### Build dengan GUI:
1. Buka aplikasi `python main_enhanced.py`
2. Tab "Build" → Browse → Pilih `hello.py`
3. Output Format: `binary` (Linux) / `exe` (Windows) / `app` (macOS)
4. Klik "Build"
5. Cek hasil di folder `output/`

---

## 📁 Buat Project Baru

### Console App
```bash
# Di GUI: Tab "Project Templates"
Project Name: my_console_app
Template: console
Output Path: /path/to/projects
→ Create Project
```

### Web App
```bash
# Di GUI: Tab "Project Templates"
Project Name: my_web_app
Template: web
Output Path: /path/to/projects
→ Create Project
```

---

## 🔍 Analisis Project

### Dependency Analysis
```bash
# Di GUI: Tab "Dependency Analysis"
Project Path: /path/to/project
→ Analyze Project
→ Generate Requirements
→ Validate Dependencies
```

### Project Validation
```bash
# Di GUI: Tab "Project Validation"
Project Path: /path/to/project
→ Validate Structure
→ Generate Report
→ Fix Structure (jika diperlukan)
```

---

## 🛠️ Build dengan Validasi

### Enhanced Build
```bash
# Di GUI: Tab "Build"
File: src/main.py (dari project template)
Output Format: binary
Auto Validation: ✅ (aktifkan)
→ Build
```

### Build Log
```
VALIDATION REPORT: ✅ 92%
DEPENDENCY ANALYSIS: ✅ 8 external deps
BUILD LOG: ✅ Success - output/app (7.8MB)
```

---

## 📊 Template Examples

### Console Template
```python
import click

@click.command()
@click.option('--name', default='World')
def main(name):
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

### GUI Template
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

### Web Template
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return {"message": "Hello World"}

def main():
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
```

---

## 🔧 Troubleshooting Quick Fix

### Error: PyInstaller not found
```bash
pip install pyinstaller
```

### Error: File tidak valid
```bash
# Test file Python
python -m py_compile your_file.py
```

### Error: Dependencies missing
```bash
pip install -r requirements.txt
```

### Error: Permission denied
```bash
# Linux/Mac
chmod +w output/
# Windows: Run as Administrator
```

---

## 📚 Next Steps

1. **Baca WORKFLOW.md** - Petunjuk lengkap
2. **Baca README.md** - Dokumentasi detail
3. **Explore Templates** - Coba semua template
4. **Customize Build** - Sesuaikan konfigurasi
5. **Contribute** - Bantu pengembangan

---

## 🎯 Pro Tips

- ✅ Gunakan virtual environment
- ✅ Aktifkan auto validation
- ✅ Cek dependencies sebelum build
- ✅ Gunakan `--strip` untuk ukuran kecil
- ✅ Test executable setelah build

---

**PyCraft Studio Enhanced** - Dari script ke executable dalam hitungan menit! ⚡🐍 