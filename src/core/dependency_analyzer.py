"""
Tujuan: Analisis dependencies pada proyek Python
Dependensi: ast, os, typing
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: analyzer = DependencyAnalyzer().analyze_project("project_dir")
"""

import ast
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import pkg_resources
except ImportError:
    # Fallback untuk Python 3.12+ yang tidak memiliki pkg_resources
    pkg_resources = None

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Menganalisis dependencies proyek Python."""

    def __init__(self):
        self.standard_libs = self._get_standard_libs()
        self.import_patterns = {
            "import": r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)",
            "from_import": r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import",
        }

    def _get_standard_libs(self) -> Set[str]:
        """Mendapatkan daftar library standar Python."""
        return set(sys.stdlib_module_names)

    def analyze_project(self, project_path: str) -> Dict[str, any]:
        """
        Menganalisis dependencies proyek.

        Args:
            project_path: Path ke proyek.

        Returns:
            Dictionary berisi hasil analisis.
        """
        try:
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                logger.error(f"Path tidak ditemukan: {project_path}")
                return {}

            # Analisis file Python
            python_files = list(project_path_obj.rglob("*.py"))
            imports = self._extract_imports_from_files(python_files)

            # Analisis requirements.txt jika ada
            requirements = self._analyze_requirements_file(project_path_obj)

            # Analisis setup.py jika ada
            setup_deps = self._analyze_setup_file(project_path_obj)

            # Gabungkan semua dependencies
            all_dependencies = self._merge_dependencies(
                imports, requirements, setup_deps
            )

            return {
                "project_path": str(project_path_obj),
                "python_files": len(python_files),
                "imports": imports,
                "requirements": requirements,
                "setup_dependencies": setup_deps,
                "all_dependencies": all_dependencies,
                "missing_dependencies": self._find_missing_dependencies(
                    all_dependencies
                ),
                "recommendations": self._generate_recommendations(all_dependencies),
            }

        except Exception as e:
            logger.error(f"Error saat menganalisis proyek: {e}")
            return {}

    def _extract_imports_from_files(
        self, python_files: List[Path]
    ) -> Dict[str, Set[str]]:
        """Mengekstrak import dari file Python."""
        imports = {"external": set(), "internal": set(), "standard": set()}

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_imports = self._parse_imports(content)

                for imp in file_imports:
                    if imp in self.standard_libs:
                        imports["standard"].add(imp)
                    elif self._is_internal_import(imp, file_path):
                        imports["internal"].add(imp)
                    else:
                        imports["external"].add(imp)

            except Exception as e:
                logger.warning(f"Error saat parsing file {file_path}: {e}")
                continue
        # Mapping khusus agar builder lebih cerdas
        if "PIL" in imports["external"]:
            imports["external"].add("pillow")
        if "tkinter" in imports["external"]:
            imports["external"].add("tkinter")
        if "ttkbootstrap" in imports["external"]:
            imports["external"].add("ttkbootstrap")
        return imports

    def _parse_imports(self, content: str) -> Set[str]:
        """Parse import statements dari content."""
        imports = set()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

        except (SyntaxError, ValueError):
            # Fallback ke regex parsing jika AST gagal
            imports = self._parse_imports_regex(content)

        return imports

    def _parse_imports_regex(self, content: str) -> Set[str]:
        """Parse import menggunakan regex sebagai fallback."""
        imports = set()

        for line in content.split("\n"):
            line = line.strip()

            # Import statement
            match = re.match(self.import_patterns["import"], line)
            if match:
                module = match.group(1).split(".")[0]
                imports.add(module)
                continue

            # From import statement
            match = re.match(self.import_patterns["from_import"], line)
            if match:
                module = match.group(1).split(".")[0]
                imports.add(module)

        return imports

    def _is_internal_import(self, module: str, file_path: Path) -> bool:
        """Mengecek apakah import adalah internal."""
        # Implementasi sederhana - bisa ditingkatkan
        return module.startswith(".") or module in ["src", "tests", "config"]

    def _analyze_requirements_file(self, project_path: Path) -> Dict[str, str]:
        """Menganalisis file requirements.txt."""
        requirements_file = project_path / "requirements.txt"

        if not requirements_file.exists():
            return {}

        dependencies = {}

        try:
            with open(requirements_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse dependency
                        dep_info = self._parse_requirement_line(line)
                        if dep_info:
                            dependencies[dep_info[0]] = dep_info[1]

        except Exception as e:
            logger.warning(f"Error saat membaca requirements.txt: {e}")

        return dependencies

    def _parse_requirement_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse baris requirements.txt."""
        # Remove comments
        line = line.split("#")[0].strip()
        if not line:
            return None

        # Parse package name and version
        if "==" in line:
            name, version = line.split("==", 1)
        elif ">=" in line:
            name, version = line.split(">=", 1)
        elif "<=" in line:
            name, version = line.split("<=", 1)
        elif "~=" in line:
            name, version = line.split("~=", 1)
        else:
            name, version = line, "latest"

        return name.strip(), version.strip()

    def _analyze_setup_file(self, project_path: Path) -> Dict[str, str]:
        """Menganalisis file setup.py."""
        setup_file = project_path / "setup.py"

        if not setup_file.exists():
            return {}

        dependencies = {}

        try:
            with open(setup_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple regex parsing untuk install_requires
            pattern = r"install_requires\s*=\s*\[(.*?)\]"
            match = re.search(pattern, content, re.DOTALL)

            if match:
                requires_str = match.group(1)
                # Parse dependencies dari string
                deps = re.findall(r'["\']([^"\']+)["\']', requires_str)
                for dep in deps:
                    dep_info = self._parse_requirement_line(dep)
                    if dep_info:
                        dependencies[dep_info[0]] = dep_info[1]

        except Exception as e:
            logger.warning(f"Error saat membaca setup.py: {e}")

        return dependencies

    def _merge_dependencies(
        self,
        imports: Dict[str, Set[str]],
        requirements: Dict[str, str],
        setup_deps: Dict[str, str],
    ) -> Dict[str, str]:
        """Menggabungkan semua dependencies."""
        merged = {}

        # Add requirements
        merged.update(requirements)

        # Add setup dependencies
        merged.update(setup_deps)

        # Add external imports yang belum ada
        for imp in imports.get("external", set()):
            if imp not in merged:
                merged[imp] = "latest"

        return merged

    def _find_missing_dependencies(self, dependencies: Dict[str, str]) -> List[str]:
        """Mencari dependencies yang tidak terinstall."""
        missing = []

        if pkg_resources is None:
            # Jika pkg_resources tidak tersedia, skip validation
            return missing

        for package in dependencies.keys():
            try:
                pkg_resources.get_distribution(package)
            except pkg_resources.DistributionNotFound:
                missing.append(package)

        return missing

    def _generate_recommendations(self, dependencies: Dict[str, str]) -> List[str]:
        """Menggenerate rekomendasi untuk proyek."""
        recommendations = []

        # Check untuk dependencies yang umum
        common_deps = {
            "requests": "HTTP library untuk API calls",
            "pandas": "Data manipulation dan analysis",
            "numpy": "Numerical computing",
            "matplotlib": "Plotting dan visualization",
            "pytest": "Testing framework",
            "black": "Code formatter",
            "flake8": "Linting tool",
        }

        for dep, description in common_deps.items():
            if dep not in dependencies:
                recommendations.append(
                    f"Pertimbangkan menambahkan {dep}: {description}"
                )

        # Check untuk security
        if "requests" in dependencies and "urllib3" not in dependencies:
            recommendations.append(
                "requests membutuhkan urllib3 untuk security updates"
            )

        return recommendations

    def generate_requirements_txt(
        self, project_path: str, output_path: Optional[str] = None
    ) -> bool:
        """
        Generate requirements.txt otomatis.

        Args:
            project_path: Path ke proyek.
            output_path: Path untuk output requirements.txt.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            analysis = self.analyze_project(project_path)

            if not analysis:
                return False

            if output_path is None:
                output_path_obj = Path(project_path) / "requirements.txt"
            else:
                output_path_obj = Path(output_path)

            # Generate content
            content = "# Auto-generated requirements.txt\n"
            content += "# Generated by PyCraft Studio\n\n"

            # Add dependencies
            for package, version in analysis["all_dependencies"].items():
                if version == "latest":
                    content += f"{package}\n"
                else:
                    content += f"{package}>={version}\n"

            # Write file
            with open(output_path_obj, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"requirements.txt berhasil dibuat: {output_path_obj}")
            return True

        except Exception as e:
            logger.error(f"Error saat generate requirements.txt: {e}")
            return False

    def validate_dependencies(self, project_path: str) -> Dict[str, any]:
        """
        Memvalidasi dependencies proyek.

        Args:
            project_path: Path ke proyek.

        Returns:
            Dictionary berisi hasil validasi.
        """
        try:
            analysis = self.analyze_project(project_path)

            if not analysis:
                return {}

            # Check compatibility
            compatibility_issues = self._check_compatibility(
                analysis["all_dependencies"]
            )

            # Check security
            security_issues = self._check_security(analysis["all_dependencies"])

            return {
                "valid": len(analysis["missing_dependencies"]) == 0,
                "missing_dependencies": analysis["missing_dependencies"],
                "compatibility_issues": compatibility_issues,
                "security_issues": security_issues,
                "recommendations": analysis["recommendations"],
            }

        except Exception as e:
            logger.error(f"Error saat validasi dependencies: {e}")
            return {}

    def _check_compatibility(self, dependencies: Dict[str, str]) -> List[str]:
        """Mengecek kompatibilitas dependencies."""
        issues = []

        # Check Python version compatibility
        python_version = sys.version_info

        # Check untuk dependencies yang mungkin bermasalah
        problematic_deps = {
            "tensorflow": "Membutuhkan Python 3.7-3.11",
            "torch": "Membutuhkan Python 3.8+",
            "django": "Membutuhkan Python 3.8+",
        }

        for dep, requirement in problematic_deps.items():
            if dep in dependencies:
                if python_version < (3, 8):
                    issues.append(f"{dep}: {requirement}")

        return issues

    def _check_security(self, dependencies: Dict[str, str]) -> List[str]:
        """Mengecek masalah security dependencies."""
        issues = []

        # Check untuk dependencies yang diketahui bermasalah
        vulnerable_deps = {
            "urllib3": "Versi < 1.26.0 memiliki vulnerability",
            "requests": "Versi < 2.25.0 memiliki vulnerability",
            "cryptography": "Versi < 3.3.0 memiliki vulnerability",
        }

        for dep, issue in vulnerable_deps.items():
            if dep in dependencies:
                version = dependencies[dep]
                if version != "latest" and self._is_vulnerable_version(dep, version):
                    issues.append(f"{dep}: {issue}")

        return issues

    def _is_vulnerable_version(self, package: str, version: str) -> bool:
        """Mengecek apakah versi package vulnerable."""
        # Implementasi sederhana - bisa ditingkatkan dengan database CVE
        vulnerable_versions = {
            "urllib3": ["1.25.0", "1.24.0", "1.23.0"],
            "requests": ["2.24.0", "2.23.0", "2.22.0"],
            "cryptography": ["3.2.0", "3.1.0", "3.0.0"],
        }

        if package in vulnerable_versions:
            return version in vulnerable_versions[package]

        return False
