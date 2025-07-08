# Panduan Membuat Installer PyCraft Studio

---

## 1. Windows: Membuat Installer .exe dengan NSIS

### A. Build executable
1. Build aplikasi dengan PyCraft Studio (output: folder dist/ atau output/ berisi .exe).

### B. Install NSIS
- Download dan install NSIS: https://nsis.sourceforge.io/Download

### C. Contoh Skrip NSIS (pycraft_installer.nsi)
```nsi
Outfile "PyCraftStudioSetup.exe"
InstallDir "$PROGRAMFILES\PyCraftStudio"
Page directory
Page instfiles
Section "Install"
  SetOutPath $INSTDIR
  File /r "output\*.*"
  CreateShortCut "$DESKTOP\PyCraft Studio.lnk" "$INSTDIR\pycraft_studio.exe"
SectionEnd
```

### D. Compile Skrip
- Buka NSIS, pilih skrip .nsi, klik Compile.
- Hasil: PyCraftStudioSetup.exe siap didistribusikan.

---

## 2. Linux: Membuat Paket .deb

### A. Struktur Folder
```
pycraftstudio/
├── DEBIAN/
│   └── control
└── usr/
    └── local/
        └── bin/
            └── pycraft_studio
```

### B. File control (DEBIAN/control)
```
Package: pycraftstudio
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Nama Anda <email@domain.com>
Description: PyCraft Studio - Python Project Builder
```

### C. Build Paket
```bash
dpkg-deb --build pycraftstudio
```

---

## 3. Mac: Membuat .dmg

### A. Build executable (output: .app atau binary)
### B. Gunakan create-dmg atau hdiutil
```bash
npm install -g create-dmg
create-dmg path/to/PyCraftStudio.app
```
Atau:
```bash
hdiutil create -volname "PyCraft Studio" -srcfolder path/to/PyCraftStudio.app -ov -format UDZO PyCraftStudio.dmg
```

---

## 4. Tips Distribusi
- Sertakan README dan LICENSE di installer.
- Uji installer di VM/OS target sebelum rilis.
- Untuk multiplatform, hasilkan installer di masing-masing OS atau gunakan CI/CD cloud build. 