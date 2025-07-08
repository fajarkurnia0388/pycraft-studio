"""
Tujuan: Enhanced builder dengan validasi, analisis dependencies, dan optimasi build
Dependensi: src.core.builder, src.core.build_validator, src.core.dependency_analyzer
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: builder = EnhancedProjectBuilder().build_with_validation("project_dir", "exe")
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .builder import ProjectBuilder, BuildResult, BuildStatus
from .project_templates import ProjectTemplateGenerator
from .dependency_analyzer import DependencyAnalyzer
from .build_validator import BuildConfigValidator
from ..utils.performance import performance_decorator, build_tracker

logger = logging.getLogger(__name__)


class EnhancedProjectBuilder(ProjectBuilder):
    """Enhanced builder dengan validasi dan optimasi otomatis."""
    
    def __init__(self, output_directory: Optional[str] = None):
        super().__init__(output_directory)
        self.template_generator = ProjectTemplateGenerator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.build_validator = BuildConfigValidator()
        
        # Enhanced build status
        self.validation_status = "pending"
        self.optimization_status = "pending"
        self.dependency_status = "pending"
    
    def create_project_from_template(self, project_name: str, template_name: str, 
                                   output_path: str) -> Dict[str, Any]:
        """
        Membuat proyek baru dari template.
        
        Args:
            project_name: Nama proyek.
            template_name: Jenis template.
            output_path: Path untuk output.
            
        Returns:
            Dictionary berisi hasil pembuatan proyek.
        """
        try:
            logger.info(f"Membuat proyek {project_name} dengan template {template_name}")
            
            # Validasi template
            if template_name not in self.template_generator.get_available_templates():
                return {
                    "success": False,
                    "error": f"Template tidak ditemukan: {template_name}",
                    "available_templates": self.template_generator.get_available_templates()
                }
            
            # Buat proyek
            success = self.template_generator.create_project(
                project_name, template_name, output_path
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Gagal membuat proyek"
                }
            
            project_path = Path(output_path) / project_name
            
            # Analisis dependencies otomatis
            dependency_analysis = self.dependency_analyzer.analyze_project(str(project_path))
            
            # Validasi struktur
            validation = self.build_validator.validate_project_structure(str(project_path))
            
            return {
                "success": True,
                "project_path": str(project_path),
                "template_info": self.template_generator.get_template_info(template_name),
                "dependency_analysis": dependency_analysis,
                "validation": validation,
                "next_steps": self._get_next_steps(validation, dependency_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error saat membuat proyek: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @performance_decorator(build_tracker.monitor)
    def build_with_validation(self, project_path: str, output_format: str,
                             additional_args: Optional[List[str]] = None) -> BuildResult:
        """
        Build dengan validasi lengkap.
        
        Args:
            project_path: Path ke proyek.
            output_format: Format output.
            additional_args: Argumen tambahan.
            
        Returns:
            BuildResult dengan informasi validasi.
        """
        try:
            logger.info(f"Memulai build dengan validasi untuk {project_path}")
            
            # 1. Validasi struktur proyek
            validation_result = self.build_validator.validate_project_structure(project_path)
            self.validation_status = "completed"
            
            if not validation_result["valid"]:
                logger.warning("Validasi struktur proyek gagal")
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message=f"Validasi gagal: {validation_result['errors']}",
                    build_time=0,
                    status=BuildStatus.FAILED,
                    log_output=f"Validation Report:\n{self.build_validator.get_validation_report(project_path)}"
                )
            
            # 2. Analisis dependencies
            dependency_analysis = self.dependency_analyzer.analyze_project(project_path)
            self.dependency_status = "completed"
            
            # 3. Validasi dependencies
            dependency_validation = self.dependency_analyzer.validate_dependencies(project_path)
            
            if not dependency_validation.get("valid", True):
                logger.warning("Validasi dependencies gagal")
                missing_deps = dependency_validation.get("missing_dependencies", [])
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message=f"Dependencies tidak lengkap: {missing_deps}",
                    build_time=0,
                    status=BuildStatus.FAILED,
                    log_output=f"Dependency Analysis:\n{self._format_dependency_report(dependency_analysis)}"
                )
            
            # 4. Optimasi build
            optimized_args = self._optimize_build_args(additional_args, dependency_analysis)
            self.optimization_status = "completed"
            
            # 5. Build executable
            logger.info("Memulai build executable")
            
            # Find main.py in project
            main_file = Path(project_path) / "src" / "main.py"
            if not main_file.exists():
                main_file = Path(project_path) / "main.py"
            
            if not main_file.exists():
                return BuildResult(
                    success=False,
                    output_path=None,
                    error_message="Main file tidak ditemukan (src/main.py atau main.py)",
                    build_time=0,
                    status=BuildStatus.FAILED,
                    log_output=""
                )
            
            build_result = super().build(str(main_file), output_format, optimized_args)
            
            # 6. Tambahkan informasi validasi ke hasil
            build_result.log_output = f"""
VALIDATION REPORT:
{self.build_validator.get_validation_report(project_path)}

DEPENDENCY ANALYSIS:
{self._format_dependency_report(dependency_analysis)}

BUILD LOG:
{build_result.log_output}
"""
            
            return build_result
            
        except Exception as e:
            logger.error(f"Error saat build dengan validasi: {e}")
            return BuildResult(
                success=False,
                output_path=None,
                error_message=str(e),
                build_time=0,
                status=BuildStatus.FAILED,
                log_output=""
            )
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analisis lengkap proyek.
        
        Args:
            project_path: Path ke proyek.
            
        Returns:
            Dictionary berisi hasil analisis lengkap.
        """
        try:
            logger.info(f"Menganalisis proyek: {project_path}")
            
            # Analisis dependencies
            dependency_analysis = self.dependency_analyzer.analyze_project(project_path)
            
            # Validasi struktur
            validation = self.build_validator.validate_project_structure(project_path)
            
            # Validasi dependencies
            dependency_validation = self.dependency_analyzer.validate_dependencies(project_path)
            
            # Rekomendasi optimasi
            optimization_recommendations = self._get_optimization_recommendations(
                dependency_analysis, validation
            )
            
            return {
                "project_path": project_path,
                "dependency_analysis": dependency_analysis,
                "structure_validation": validation,
                "dependency_validation": dependency_validation,
                "optimization_recommendations": optimization_recommendations,
                "overall_score": self._calculate_overall_score(validation, dependency_validation),
                "build_readiness": self._assess_build_readiness(validation, dependency_validation)
            }
            
        except Exception as e:
            logger.error(f"Error saat analisis proyek: {e}")
            return {"error": str(e)}
    
    def generate_project_report(self, project_path: str) -> str:
        """
        Generate laporan lengkap proyek.
        
        Args:
            project_path: Path ke proyek.
            
        Returns:
            String berisi laporan lengkap.
        """
        try:
            analysis = self.analyze_project(project_path)
            
            if "error" in analysis:
                return f"Error: {analysis['error']}"
            
            report = f"""
LAPORAN ANALISIS PROYEK
=======================
Path: {project_path}
Overall Score: {analysis['overall_score']}%
Build Readiness: {analysis['build_readiness']}

{self.build_validator.get_validation_report(project_path)}

DEPENDENCY ANALYSIS:
{self._format_dependency_report(analysis['dependency_analysis'])}

DEPENDENCY VALIDATION:
{self._format_dependency_validation(analysis['dependency_validation'])}

OPTIMIZATION RECOMMENDATIONS:
{self._format_optimization_recommendations(analysis['optimization_recommendations'])}

NEXT STEPS:
{self._get_next_steps(analysis['structure_validation'], analysis['dependency_analysis'])}
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error saat generate laporan: {e}")
            return f"Error: {e}"
    
    def _optimize_build_args(self, additional_args: Optional[List[str]], 
                           dependency_analysis: Dict[str, Any]) -> List[str]:
        """Optimasi argumen build berdasarkan analisis dependencies."""
        optimized_args = additional_args or []
        
        # Optimasi berdasarkan dependencies
        external_deps = dependency_analysis.get("imports", {}).get("external", set())
        
        # Jika ada GUI dependencies, tambahkan --windowed
        gui_deps = {'tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx'}
        if any(dep in gui_deps for dep in external_deps):
            if '--windowed' not in optimized_args:
                optimized_args.append('--windowed')
        
        # Jika ada data dependencies, tambahkan --add-data
        data_deps = {'pandas', 'numpy', 'matplotlib', 'seaborn'}
        if any(dep in data_deps for dep in external_deps):
            if '--add-data' not in str(optimized_args):
                optimized_args.extend(['--add-data', 'resources:resources'])
        
        # Optimasi ukuran
        if '--strip' not in optimized_args:
            optimized_args.append('--strip')
        
        return optimized_args
    
    def _get_optimization_recommendations(self, dependency_analysis: Dict[str, Any],
                                        validation: Dict[str, Any]) -> List[str]:
        """Mendapatkan rekomendasi optimasi."""
        recommendations = []
        
        # Rekomendasi berdasarkan dependencies
        external_deps = dependency_analysis.get("imports", {}).get("external", set())
        
        if 'requests' in external_deps:
            recommendations.append("Pertimbangkan menggunakan --exclude-module untuk mengurangi ukuran")
        
        if len(external_deps) > 10:
            recommendations.append("Banyak dependencies - pertimbangkan virtual environment")
        
        # Rekomendasi berdasarkan validasi
        if validation.get("score", 0) < 80:
            recommendations.append("Tingkatkan struktur proyek untuk performa build yang lebih baik")
        
        return recommendations
    
    def _calculate_overall_score(self, validation: Dict[str, Any],
                               dependency_validation: Dict[str, Any]) -> int:
        """Hitung overall score proyek."""
        structure_score = validation.get("score", 0)
        dependency_score = 100 if dependency_validation.get("valid", False) else 50
        
        return int((structure_score + dependency_score) / 2)
    
    def _assess_build_readiness(self, validation: Dict[str, Any],
                              dependency_validation: Dict[str, Any]) -> str:
        """Assess kesiapan build."""
        if not validation.get("valid", False):
            return "NOT READY - Struktur proyek tidak valid"
        
        if not dependency_validation.get("valid", False):
            return "NOT READY - Dependencies tidak lengkap"
        
        score = validation.get("score", 0)
        if score >= 90:
            return "EXCELLENT"
        elif score >= 80:
            return "GOOD"
        elif score >= 70:
            return "FAIR"
        else:
            return "POOR"
    
    def _format_dependency_report(self, dependency_analysis: Dict[str, Any]) -> str:
        """Format laporan dependencies."""
        if not dependency_analysis:
            return "Tidak ada data dependencies"
        
        report = f"""
Total Python Files: {dependency_analysis.get('python_files', 0)}

External Dependencies: {len(dependency_analysis.get('imports', {}).get('external', set()))}
Standard Libraries: {len(dependency_analysis.get('imports', {}).get('standard', set()))}
Internal Modules: {len(dependency_analysis.get('imports', {}).get('internal', set()))}

Dependencies:
"""
        
        all_deps = dependency_analysis.get("all_dependencies", {})
        for package, version in all_deps.items():
            report += f"  - {package}: {version}\n"
        
        recommendations = dependency_analysis.get("recommendations", [])
        if recommendations:
            report += "\nRecommendations:\n"
            for rec in recommendations:
                report += f"  - {rec}\n"
        
        return report
    
    def _format_dependency_validation(self, validation: Dict[str, Any]) -> str:
        """Format validasi dependencies."""
        if not validation:
            return "Tidak ada data validasi"
        
        report = f"Valid: {validation.get('valid', False)}\n"
        
        missing = validation.get("missing_dependencies", [])
        if missing:
            report += f"Missing: {', '.join(missing)}\n"
        
        issues = validation.get("compatibility_issues", [])
        if issues:
            report += f"Compatibility Issues: {', '.join(issues)}\n"
        
        security = validation.get("security_issues", [])
        if security:
            report += f"Security Issues: {', '.join(security)}\n"
        
        return report
    
    def _format_optimization_recommendations(self, recommendations: List[str]) -> str:
        """Format rekomendasi optimasi."""
        if not recommendations:
            return "Tidak ada rekomendasi optimasi"
        
        report = ""
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def _get_next_steps(self, validation: Dict[str, Any],
                       dependency_analysis: Dict[str, Any]) -> str:
        """Mendapatkan langkah selanjutnya."""
        steps = []
        
        if not validation.get("valid", False):
            steps.append("1. Perbaiki struktur proyek sesuai validasi")
        
        missing_deps = dependency_analysis.get("missing_dependencies", [])
        if missing_deps:
            steps.append(f"2. Install dependencies yang hilang: {', '.join(missing_deps)}")
        
        if validation.get("score", 0) < 80:
            steps.append("3. Ikuti rekomendasi untuk meningkatkan struktur proyek")
        
        if not steps:
            steps.append("1. Proyek siap untuk build!")
        
        return "\n".join(steps)
    
    def get_available_templates(self) -> List[str]:
        """Mendapatkan daftar template yang tersedia."""
        return self.template_generator.get_available_templates()
    
    def get_template_info(self, template_name: str):
        """Mendapatkan informasi template."""
        return self.template_generator.get_template_info(template_name) 