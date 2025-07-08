"""
Tujuan: Validasi struktur dan kualitas proyek Python
Dependensi: os, typing, logging
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: validator = BuildConfigValidator().validate_project("project_dir")
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BuildConfigValidator:
    """Memvalidasi konfigurasi build dan struktur proyek."""
    
    def __init__(self):
        self.required_files = [
            "src/main.py",
            "requirements.txt",
            "README.md"
        ]
        
        self.recommended_files = [
            "tests/",
            "docs/",
            ".gitignore",
            "setup.py",
            "pyproject.toml"
        ]
        
        self.best_practices = [
            "src/__init__.py",
            "tests/__init__.py",
            "config/__init__.py"
        ]
    
    def validate_project_structure(self, project_path: str) -> Dict[str, any]:
        """
        Memvalidasi struktur proyek.
        
        Args:
            project_path: Path ke proyek.
            
        Returns:
            Dictionary berisi hasil validasi.
        """
        try:
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                logger.error(f"Path tidak ditemukan: {project_path}")
                return {"valid": False, "errors": ["Path tidak ditemukan"]}
            
            results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "recommendations": [],
                "score": 0,
                "total_checks": 0
            }
            
            # Validasi file wajib
            self._validate_required_files(project_path_obj, results)
            
            # Validasi file yang direkomendasikan
            self._validate_recommended_files(project_path_obj, results)
            
            # Validasi best practices
            self._validate_best_practices(project_path_obj, results)
            
            # Validasi entry point
            self._validate_entry_point(project_path_obj, results)
            
            # Hitung score
            results["score"] = self._calculate_score(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error saat validasi struktur proyek: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    def _validate_required_files(self, project_path: Path, results: Dict):
        """Validasi file-file wajib."""
        for file_path in self.required_files:
            results["total_checks"] += 1
            full_path = project_path / file_path
            
            if full_path.exists():
                results["score"] += 1
            else:
                results["errors"].append(f"File wajib tidak ditemukan: {file_path}")
                results["valid"] = False
    
    def _validate_recommended_files(self, project_path: Path, results: Dict):
        """Validasi file-file yang direkomendasikan."""
        for file_path in self.recommended_files:
            results["total_checks"] += 1
            full_path = project_path / file_path
            
            if full_path.exists():
                results["score"] += 1
            else:
                results["warnings"].append(f"File direkomendasikan tidak ditemukan: {file_path}")
    
    def _validate_best_practices(self, project_path: Path, results: Dict):
        """Validasi best practices."""
        for file_path in self.best_practices:
            results["total_checks"] += 1
            full_path = project_path / file_path
            
            if full_path.exists():
                results["score"] += 1
            else:
                results["recommendations"].append(f"Best practice: tambahkan {file_path}")
    
    def _validate_entry_point(self, project_path: Path, results: Dict):
        """Validasi entry point."""
        main_file = project_path / "src" / "main.py"
        
        if not main_file.exists():
            results["errors"].append("Entry point tidak ditemukan: src/main.py")
            results["valid"] = False
            return
        
        # Validasi struktur main.py
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check untuk main function
            if 'def main():' in content or 'def main(' in content:
                results["score"] += 1
            else:
                results["warnings"].append("Main function tidak ditemukan di src/main.py")
            
            # Check untuk if __name__ == "__main__"
            if 'if __name__ == "__main__":' in content:
                results["score"] += 1
            else:
                results["warnings"].append("Entry point guard tidak ditemukan di src/main.py")
            
            # Check untuk docstring
            if '"""' in content or "'''" in content:
                results["score"] += 1
            else:
                results["recommendations"].append("Tambahkan docstring di src/main.py")
            
            results["total_checks"] += 3
            
        except Exception as e:
            results["errors"].append(f"Error saat membaca src/main.py: {e}")
            results["valid"] = False
    
    def _calculate_score(self, results: Dict) -> int:
        """Hitung score validasi."""
        if results["total_checks"] == 0:
            return 0
        
        return int((results["score"] / results["total_checks"]) * 100)
    
    def validate_entry_point(self, main_file: str) -> Dict[str, any]:
        """
        Memvalidasi entry point.
        
        Args:
            main_file: Path ke file main.
            
        Returns:
            Dictionary berisi hasil validasi.
        """
        try:
            main_path = Path(main_file)
            if not main_path.exists():
                return {"valid": False, "errors": ["File tidak ditemukan"]}
            
            results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "recommendations": []
            }
            
            with open(main_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, results)
            except SyntaxError as e:
                results["errors"].append(f"Syntax error: {e}")
                results["valid"] = False
            
            # Check patterns
            self._check_patterns(content, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error saat validasi entry point: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    def _analyze_ast(self, tree: ast.AST, results: Dict):
        """Analisis AST untuk validasi."""
        has_main_function = False
        has_main_call = False
        
        for node in ast.walk(tree):
            # Check untuk main function
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                has_main_function = True
                
                # Check untuk docstring
                if ast.get_docstring(node):
                    results["score"] = results.get("score", 0) + 1
                else:
                    results["recommendations"].append("Tambahkan docstring di main function")
            
            # Check untuk main call
            elif isinstance(node, ast.If):
                if (isinstance(node.test, ast.Compare) and 
                    isinstance(node.test.left, ast.Name) and 
                    node.test.left.id == "__name__"):
                    has_main_call = True
        
        if not has_main_function:
            results["warnings"].append("Main function tidak ditemukan")
        
        if not has_main_call:
            results["warnings"].append("Entry point guard tidak ditemukan")
    
    def _check_patterns(self, content: str, results: Dict):
        """Check patterns dalam content."""
        # Check untuk imports
        if not re.search(r'^import\s+\w+', content, re.MULTILINE) and \
           not re.search(r'^from\s+\w+\s+import', content, re.MULTILINE):
            results["warnings"].append("Tidak ada import statements")
        
        # Check untuk logging
        if 'logging' in content or 'logger' in content:
            results["score"] = results.get("score", 0) + 1
        else:
            results["recommendations"].append("Pertimbangkan menambahkan logging")
        
        # Check untuk error handling
        if 'try:' in content and 'except:' in content:
            results["score"] = results.get("score", 0) + 1
        else:
            results["recommendations"].append("Pertimbangkan menambahkan error handling")
    
    def generate_project_structure(self, project_path: str, 
                                  project_type: str = "standard") -> bool:
        """
        Generate struktur proyek standar.
        
        Args:
            project_path: Path ke proyek.
            project_type: Jenis proyek.
            
        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            project_path_obj = Path(project_path)
            
            # Buat direktori utama
            project_path_obj.mkdir(parents=True, exist_ok=True)
            
            # Buat struktur direktori
            directories = [
                "src",
                "tests",
                "docs",
                "config",
                "resources"
            ]
            
            for directory in directories:
                (project_path_obj / directory).mkdir(exist_ok=True)
                (project_path_obj / directory / "__init__.py").touch()
            
            # Buat file-file standar
            self._create_standard_files(project_path_obj, project_type)
            
            logger.info(f"Struktur proyek berhasil dibuat: {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saat membuat struktur proyek: {e}")
            return False
    
    def _create_standard_files(self, project_path: Path, project_type: str):
        """Membuat file-file standar."""
        
        # main.py
        main_content = '''"""
Main entry point aplikasi.

Auto-generated oleh PyCraft Studio.
"""

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function."""
    logger.info("Aplikasi dimulai")
    
    try:
        # Logika utama aplikasi
        print("Hello, World!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    logger.info("Aplikasi selesai")
    return 0


if __name__ == "__main__":
    exit(main())
'''
        
        (project_path / "src" / "main.py").write_text(main_content)
        
        # requirements.txt
        requirements_content = """# Dependencies
# Tambahkan dependencies proyek di sini

# Development dependencies
pytest>=6.0.0
black>=21.0.0
flake8>=3.8.0
"""
        
        (project_path / "requirements.txt").write_text(requirements_content)
        
        # README.md
        readme_content = f"""# {project_path.name}

Deskripsi proyek.

## Instalasi

```bash
pip install -r requirements.txt
```

## Penggunaan

```bash
python src/main.py
```

## Testing

```bash
pytest tests/
```

## Struktur Proyek

```
{project_path.name}/
├── src/           # Kode sumber
├── tests/         # Unit tests
├── docs/          # Dokumentasi
├── config/        # Konfigurasi
└── resources/     # Asset
```
"""
        
        (project_path / "README.md").write_text(readme_content)
        
        # .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        (project_path / ".gitignore").write_text(gitignore_content)
    
    def get_validation_report(self, project_path: str) -> str:
        """
        Mendapatkan laporan validasi dalam format text.
        
        Args:
            project_path: Path ke proyek.
            
        Returns:
            String berisi laporan validasi.
        """
        validation = self.validate_project_structure(project_path)
        
        if not validation:
            return "Error: Tidak dapat memvalidasi proyek"
        
        report = f"""
VALIDASI STRUKTUR PROYEK
========================
Path: {project_path}
Status: {'VALID' if validation['valid'] else 'INVALID'}
Score: {validation.get('score', 0)}%

ERRORS:
"""
        
        if validation['errors']:
            for error in validation['errors']:
                report += f"❌ {error}\n"
        else:
            report += "✅ Tidak ada error\n"
        
        report += "\nWARNINGS:\n"
        if validation['warnings']:
            for warning in validation['warnings']:
                report += f"⚠️  {warning}\n"
        else:
            report += "✅ Tidak ada warning\n"
        
        report += "\nRECOMMENDATIONS:\n"
        if validation['recommendations']:
            for rec in validation['recommendations']:
                report += f"💡 {rec}\n"
        else:
            report += "✅ Tidak ada rekomendasi\n"
        
        return report 