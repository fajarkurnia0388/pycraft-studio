# FAQ & Troubleshooting PyCraft Studio

---

## ❓ FAQ

**Q: Bagaimana cara menjalankan aplikasi?**
A: Jalankan dengan perintah:
```bash
python -m src.main
```

**Q: Apakah harus pakai virtual environment?**
A: Sangat disarankan untuk menghindari konflik dependency.

**Q: Bagaimana cara build executable?**
A: Buka aplikasi, tab Build, pilih file Python, pilih format output, klik Build.

**Q: Kenapa pre-commit error saat commit?**
A: Pastikan dependency pre-commit sudah benar. Jika error mypy/types-all, sementara bisa commit dengan `--no-verify` atau nonaktifkan hook tersebut.

---

## 🛠️ Troubleshooting

**1. Error: PyInstaller not found**
```bash
pip install pyinstaller
```

**2. Error: File tidak valid**
```bash
python -m py_compile your_file.py
```

**3. Error: Dependencies missing**
```bash
pip install -r requirements.txt
```

**4. Error: Permission denied**
```bash
# Linux/Mac
chmod +w output/
# Windows: Run as Administrator
```

**5. Error: pre-commit gagal (mypy/types-all)**
- Edit `.pre-commit-config.yaml` dan nonaktifkan blok mirrors-mypy.
- Atau commit dengan:
```bash
git commit -m "msg" --no-verify
```

**6. Build gagal di OS lain**
- Pastikan dependency dan path sudah benar.
- Untuk build multiplatform, gunakan Docker atau CI/CD.

---

Jika masalah belum teratasi, cek dokumentasi lengkap atau buka issue di GitHub. 