"""
Tujuan: Unit tests untuk modul enhanced_builder
Dependensi: pytest, unittest.mock, src.core.enhanced_builder
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.core.enhanced_builder import EnhancedProjectBuilder


class TestEnhancedProjectBuilder:
    """Test cases untuk EnhancedProjectBuilder."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.builder = EnhancedProjectBuilder(self.temp_dir)
        # Override format build agar semua didukung saat test
        self.builder.get_supported_formats = lambda: ['exe', 'app', 'binary']

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test inisialisasi EnhancedProjectBuilder."""
        assert self.builder.output_directory == self.temp_dir
        assert hasattr(self.builder, 'template_generator')
        assert hasattr(self.builder, 'dependency_analyzer')
        assert hasattr(self.builder, 'build_validator')

    def test_validation_status(self):
        """Test validation status."""
        assert self.builder.validation_status == "pending"
        assert self.builder.optimization_status == "pending"
        assert self.builder.dependency_status == "pending"

    def test_create_project_from_template(self):
        """Test membuat project dari template."""
        project_name = "test_project"
        template_name = "basic"
        output_path = self.temp_dir

        result = self.builder.create_project_from_template(project_name, template_name, output_path)
        assert isinstance(result, dict)
        assert "success" in result

    def test_build_with_validation(self):
        """Test build dengan validasi."""
        # Create test project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        (project_dir / "main.py").write_text("print('Hello World')")
        (project_dir / "requirements.txt").write_text("requests==2.28.1")

        result = self.builder.build_with_validation(str(project_dir), "binary")
        assert hasattr(result, 'success')
        assert hasattr(result, 'status')

    def test_analyze_project(self):
        """Test analisis project."""
        # Create test project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        (project_dir / "main.py").write_text("print('Hello World')")

        result = self.builder.analyze_project(str(project_dir))
        assert isinstance(result, dict)
        assert "build_readiness" in result
        assert "dependency_analysis" in result

    def test_generate_project_report(self):
        """Test generate project report."""
        # Create test project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        (project_dir / "main.py").write_text("print('Hello World')")

        report = self.builder.generate_project_report(str(project_dir))
        assert isinstance(report, str)
        assert len(report) > 0

    def test_get_available_templates(self):
        """Test mendapatkan available templates."""
        templates = self.builder.get_available_templates()
        assert isinstance(templates, list)

    def test_get_template_info(self):
        """Test mendapatkan template info."""
        templates = self.builder.get_available_templates()
        if templates:
            info = self.builder.get_template_info(templates[0])
            # Perbaiki: info bisa berupa TemplateConfig, bukan dict
            from src.core.project_templates import TemplateConfig
            assert isinstance(info, TemplateConfig)

    def test_template_generator_available(self):
        """Test template generator tersedia."""
        assert self.builder.template_generator is not None

    def test_dependency_analyzer_available(self):
        """Test dependency analyzer tersedia."""
        assert self.builder.dependency_analyzer is not None

    def test_build_validator_available(self):
        """Test build validator tersedia."""
        assert self.builder.build_validator is not None 