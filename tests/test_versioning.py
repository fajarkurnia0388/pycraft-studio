"""
Tujuan: Unit test untuk auto-versioning dan changelog generator
Dependensi: pytest, unittest.mock, pathlib
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import pytest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.versioning import (
    VersionManager,
    ChangelogGenerator,
    GitVersionManager,
    auto_version_from_commits,
    get_version_summary
)


class TestVersionManager:
    """Test untuk VersionManager."""
    
    def test_init_with_existing_file(self):
        """Test inisialisasi dengan file yang sudah ada."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("1.2.3")
            version_file = f.name
        
        try:
            manager = VersionManager(version_file)
            assert manager.current_version == "1.2.3"
        finally:
            Path(version_file).unlink(missing_ok=True)
    
    def test_init_without_file(self):
        """Test inisialisasi tanpa file (buat default)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            manager = VersionManager(str(version_file))
            
            assert manager.current_version == "0.1.0"
            assert version_file.exists()
            assert version_file.read_text().strip() == "0.1.0"
    
    def test_bump_version_patch(self):
        """Test bump version patch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            manager = VersionManager(str(version_file))
            new_version = manager.bump_version("patch")
            
            assert new_version == "1.2.4"
            assert manager.current_version == "1.2.4"
            assert version_file.read_text().strip() == "1.2.4"
    
    def test_bump_version_minor(self):
        """Test bump version minor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            manager = VersionManager(str(version_file))
            new_version = manager.bump_version("minor")
            
            assert new_version == "1.3.0"
            assert manager.current_version == "1.3.0"
    
    def test_bump_version_major(self):
        """Test bump version major."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            manager = VersionManager(str(version_file))
            new_version = manager.bump_version("major")
            
            assert new_version == "2.0.0"
            assert manager.current_version == "2.0.0"
    
    def test_bump_version_invalid(self):
        """Test bump version dengan tipe invalid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            manager = VersionManager(str(version_file))
            
            # Should return current version instead of raising error
            result = manager.bump_version("invalid")
            assert result == "1.2.3"  # Should return current version unchanged
    
    def test_get_version_info(self):
        """Test mendapatkan informasi versi."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            manager = VersionManager(str(version_file))
            info = manager.get_version_info()
            
            assert info["version"] == "1.2.3"
            assert "build_date" in info
            assert info["version_file"] == str(version_file)


class TestChangelogGenerator:
    """Test untuk ChangelogGenerator."""
    
    def test_init(self):
        """Test inisialisasi ChangelogGenerator."""
        with tempfile.TemporaryDirectory() as temp_dir:
            changelog_file = Path(temp_dir) / "CHANGELOG.md"
            generator = ChangelogGenerator(str(changelog_file))
            
            assert generator.changelog_file == changelog_file
            assert generator.changes == []
    
    def test_add_change(self):
        """Test menambah perubahan."""
        generator = ChangelogGenerator()
        
        generator.add_change("added", "New feature", "John Doe")
        
        assert len(generator.changes) == 1
        assert generator.changes[0]["type"] == "added"
        assert generator.changes[0]["description"] == "New feature"
        assert generator.changes[0]["author"] == "John Doe"
        assert "date" in generator.changes[0]
    
    def test_generate_changelog(self):
        """Test generate changelog."""
        generator = ChangelogGenerator()
        
        generator.add_change("added", "New feature", "John")
        generator.add_change("fixed", "Bug fix", "Jane")
        generator.add_change("changed", "Improvement", "Bob")
        
        changelog = generator.generate_changelog("1.2.3", "2025-06-24")
        
        assert "## [1.2.3] - 2025-06-24" in changelog
        assert "### Added" in changelog
        assert "### Fixed" in changelog
        assert "### Changed" in changelog
        assert "New feature (@John)" in changelog
        assert "Bug fix (@Jane)" in changelog
        assert "Improvement (@Bob)" in changelog
    
    def test_save_changelog(self):
        """Test save changelog ke file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            changelog_file = Path(temp_dir) / "CHANGELOG.md"
            generator = ChangelogGenerator(str(changelog_file))
            
            # Add existing content
            changelog_file.write_text("# Old Changelog\n\n## [0.1.0] - 2025-01-01\n\nOld content\n")
            
            generator.add_change("added", "New feature", "John")
            generator.save_changelog("1.0.0", "2025-06-24")
            
            content = changelog_file.read_text()
            assert "## [1.0.0] - 2025-06-24" in content
            assert "New feature (@John)" in content
            assert "# Old Changelog" in content
            assert "Old content" in content
    
    def test_clear_changes(self):
        """Test clear daftar perubahan."""
        generator = ChangelogGenerator()
        
        generator.add_change("added", "Feature 1", "John")
        generator.add_change("fixed", "Bug 1", "Jane")
        
        assert len(generator.changes) == 2
        
        generator.clear_changes()
        assert len(generator.changes) == 0


class TestGitVersionManager:
    """Test untuk GitVersionManager."""
    
    def test_init(self):
        """Test inisialisasi GitVersionManager."""
        version_manager = VersionManager()
        changelog_generator = ChangelogGenerator()
        
        git_manager = GitVersionManager(version_manager, changelog_generator)
        
        assert git_manager.version_manager == version_manager
        assert git_manager.changelog_generator == changelog_generator
    
    @patch('subprocess.check_output')
    def test_get_git_info(self, mock_check_output):
        """Test mendapatkan informasi Git."""
        # Mock Git commands
        mock_check_output.side_effect = [
            "main\n",  # branch
            "abc12345\n",  # commit hash
            "feat: add new feature\n"  # commit message
        ]
        
        version_manager = VersionManager()
        changelog_generator = ChangelogGenerator()
        git_manager = GitVersionManager(version_manager, changelog_generator)
        
        info = git_manager.get_git_info()
        
        assert info["branch"] == "main"
        assert info["commit_hash"] == "abc12345"
        assert info["commit_message"] == "feat: add new feature"
    
    @patch('subprocess.check_output')
    def test_get_git_info_error(self, mock_check_output):
        """Test error saat mendapatkan informasi Git."""
        mock_check_output.side_effect = Exception("Git not found")
        
        version_manager = VersionManager()
        changelog_generator = ChangelogGenerator()
        git_manager = GitVersionManager(version_manager, changelog_generator)
        
        info = git_manager.get_git_info()
        assert info == {}
    
    def test_create_release(self):
        """Test membuat release."""
        with tempfile.TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3")
            
            changelog_file = Path(temp_dir) / "CHANGELOG.md"
            
            version_manager = VersionManager(str(version_file))
            changelog_generator = ChangelogGenerator(str(changelog_file))
            git_manager = GitVersionManager(version_manager, changelog_generator)
            
            with patch.object(git_manager, 'get_git_info') as mock_git_info:
                mock_git_info.return_value = {"branch": "main", "commit_hash": "abc123"}
                
                release_info = git_manager.create_release("patch", "Test release")
                
                assert release_info is not None
                assert release_info["version"] == "1.2.4"
                assert "release_date" in release_info
                assert release_info["git_info"]["branch"] == "main"
                assert release_info["release_notes"] == "Test release"


class TestAutoVersioning:
    """Test untuk auto-versioning."""
    
    @patch('subprocess.check_output')
    def test_auto_version_from_commits(self, mock_check_output):
        """Test auto-versioning dari commit messages."""
        # Mock recent commits
        commits = [
            "abc123 feat: add new feature",
            "def456 fix: bug fix",
            "ghi789 docs: update documentation"
        ]
        mock_check_output.return_value = "\n".join(commits)
        
        with patch('src.utils.versioning.git_version_manager.create_release') as mock_create:
            mock_create.return_value = {"version": "1.1.0"}
            
            result = auto_version_from_commits()
            
            assert result["version"] == "1.1.0"
            mock_create.assert_called_once_with("patch")  # Default is patch for fix commits
    
    @patch('subprocess.check_output')
    def test_auto_version_major(self, mock_check_output):
        """Test auto-versioning untuk major bump."""
        commits = [
            "abc123 BREAKING CHANGE: major change",
            "def456 feat: new feature"
        ]
        mock_check_output.return_value = "\n".join(commits)
        
        with patch('src.utils.versioning.git_version_manager.create_release') as mock_create:
            mock_create.return_value = {"version": "2.0.0"}
            
            result = auto_version_from_commits()
            
            assert result["version"] == "2.0.0"
            mock_create.assert_called_once_with("major")
    
    @patch('subprocess.check_output')
    def test_auto_version_error(self, mock_check_output):
        """Test error saat auto-versioning."""
        mock_check_output.side_effect = Exception("Git error")
        
        result = auto_version_from_commits()
        assert result is None


class TestVersionSummary:
    """Test untuk version summary."""
    
    @patch('src.utils.versioning.version_manager.get_version_info')
    @patch('src.utils.versioning.git_version_manager.get_git_info')
    def test_get_version_summary(self, mock_git_info, mock_version_info):
        """Test mendapatkan version summary."""
        mock_version_info.return_value = {"version": "1.2.3", "build_date": "2025-06-24"}
        mock_git_info.return_value = {"branch": "main", "commit_hash": "abc123"}
        
        summary = get_version_summary()
        
        assert summary["version"] == "1.2.3"
        assert summary["build_date"] == "2025-06-24"
        assert summary["branch"] == "main"
        assert summary["commit_hash"] == "abc123"


if __name__ == "__main__":
    pytest.main([__file__]) 