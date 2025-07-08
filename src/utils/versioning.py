"""
Tujuan: Auto-versioning dan changelog generator untuk PyCraft Studio
Dependensi: re, datetime, pathlib, logging
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VersionManager:
    """Manager untuk versioning aplikasi."""
    
    def __init__(self, version_file: str = "VERSION"):
        self.version_file = Path(version_file)
        self.current_version = self._load_version()
    
    def _load_version(self) -> str:
        """Load versi dari file."""
        try:
            if self.version_file.exists():
                version = self.version_file.read_text().strip()
                logger.info(f"Loaded version: {version}")
                return version
            else:
                # Default version
                default_version = "0.1.0"
                self._save_version(default_version)
                logger.info(f"Created default version: {default_version}")
                return default_version
        except Exception as e:
            logger.error(f"Error loading version: {e}")
            return "0.1.0"
    
    def _save_version(self, version: str):
        """Save versi ke file."""
        try:
            self.version_file.write_text(version)
            logger.info(f"Saved version: {version}")
        except Exception as e:
            logger.error(f"Error saving version: {e}")
    
    def bump_version(self, bump_type: str = "patch") -> str:
        """
        Bump version berdasarkan tipe.
        
        Args:
            bump_type: 'major', 'minor', atau 'patch'
            
        Returns:
            Versi baru
        """
        try:
            major, minor, patch = map(int, self.current_version.split('.'))
            
            if bump_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump_type == "minor":
                minor += 1
                patch = 0
            elif bump_type == "patch":
                patch += 1
            else:
                raise ValueError(f"Invalid bump type: {bump_type}")
            
            new_version = f"{major}.{minor}.{patch}"
            self.current_version = new_version
            self._save_version(new_version)
            
            logger.info(f"Bumped version from {self.current_version} to {new_version}")
            return new_version
            
        except Exception as e:
            logger.error(f"Error bumping version: {e}")
            return self.current_version
    
    def get_version_info(self) -> Dict[str, str]:
        """Mendapatkan informasi versi."""
        return {
            "version": self.current_version,
            "build_date": datetime.now().isoformat(),
            "version_file": str(self.version_file)
        }


class ChangelogGenerator:
    """Generator untuk changelog."""
    
    def __init__(self, changelog_file: str = "CHANGELOG.md"):
        self.changelog_file = Path(changelog_file)
        self.changes = []
    
    def add_change(self, change_type: str, description: str, author: str = "Unknown"):
        """
        Menambah perubahan ke changelog.
        
        Args:
            change_type: 'added', 'changed', 'deprecated', 'removed', 'fixed', 'security'
            description: Deskripsi perubahan
            author: Penulis perubahan
        """
        change = {
            "type": change_type,
            "description": description,
            "author": author,
            "date": datetime.now().isoformat()
        }
        self.changes.append(change)
        logger.info(f"Added change: {change_type} - {description}")
    
    def generate_changelog(self, version: str, release_date: Optional[str] = None) -> str:
        """
        Generate changelog untuk versi tertentu.
        
        Args:
            version: Versi yang akan di-release
            release_date: Tanggal release (opsional)
            
        Returns:
            Konten changelog
        """
        if not release_date:
            release_date = datetime.now().strftime("%Y-%m-%d")
        
        changelog = f"# Changelog\n\n"
        changelog += f"## [{version}] - {release_date}\n\n"
        
        # Group changes by type
        change_types = {
            "added": [],
            "changed": [],
            "deprecated": [],
            "removed": [],
            "fixed": [],
            "security": []
        }
        
        for change in self.changes:
            change_type = change["type"].lower()
            if change_type in change_types:
                change_types[change_type].append(change)
        
        # Add changes to changelog
        for change_type, changes in change_types.items():
            if changes:
                changelog += f"### {change_type.title()}\n"
                for change in changes:
                    changelog += f"- {change['description']} (@{change['author']})\n"
                changelog += "\n"
        
        return changelog
    
    def save_changelog(self, version: str, release_date: Optional[str] = None):
        """Save changelog ke file."""
        try:
            changelog_content = self.generate_changelog(version, release_date)
            
            # Read existing changelog
            existing_content = ""
            if self.changelog_file.exists():
                existing_content = self.changelog_file.read_text()
            
            # Prepend new changelog
            full_content = changelog_content + "\n" + existing_content
            self.changelog_file.write_text(full_content)
            
            logger.info(f"Saved changelog for version {version}")
            
        except Exception as e:
            logger.error(f"Error saving changelog: {e}")
    
    def clear_changes(self):
        """Clear daftar perubahan."""
        self.changes.clear()
        logger.info("Cleared changes list")


class GitVersionManager:
    """Version manager yang terintegrasi dengan Git."""
    
    def __init__(self, version_manager: VersionManager, changelog_generator: ChangelogGenerator):
        self.version_manager = version_manager
        self.changelog_generator = changelog_generator
    
    def get_git_info(self) -> Dict[str, str]:
        """Mendapatkan informasi Git."""
        try:
            import subprocess
            
            # Get current branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                text=True
            ).strip()
            
            # Get last commit hash
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], 
                text=True
            ).strip()[:8]
            
            # Get last commit message
            commit_message = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"], 
                text=True
            ).strip()
            
            return {
                "branch": branch,
                "commit_hash": commit_hash,
                "commit_message": commit_message
            }
            
        except Exception as e:
            logger.error(f"Error getting Git info: {e}")
            return {}
    
    def create_release(self, bump_type: str = "patch", release_notes: Optional[str] = None):
        """
        Membuat release baru.
        
        Args:
            bump_type: Tipe bump version
            release_notes: Catatan release (opsional)
        """
        try:
            # Bump version
            new_version = self.version_manager.bump_version(bump_type)
            
            # Get Git info
            git_info = self.get_git_info()
            
            # Generate changelog
            self.changelog_generator.save_changelog(new_version)
            
            # Create release info
            release_info = {
                "version": new_version,
                "release_date": datetime.now().isoformat(),
                "git_info": git_info,
                "release_notes": release_notes
            }
            
            logger.info(f"Created release: {new_version}")
            return release_info
            
        except Exception as e:
            logger.error(f"Error creating release: {e}")
            return None


# Global instances
version_manager = VersionManager()
changelog_generator = ChangelogGenerator()
git_version_manager = GitVersionManager(version_manager, changelog_generator)


def auto_version_from_commits():
    """Auto-version berdasarkan commit messages."""
    try:
        import subprocess
        
        # Get recent commits
        commits = subprocess.check_output(
            ["git", "log", "--oneline", "-10"], 
            text=True
        ).strip().split('\n')
        
        # Analyze commit messages for version bump type
        bump_type = "patch"  # default
        
        for commit in commits:
            commit_msg = commit.split(' ', 1)[1] if ' ' in commit else commit
            
            # Check for breaking changes
            if "BREAKING CHANGE" in commit_msg or "major:" in commit_msg:
                bump_type = "major"
                break
            elif "feat:" in commit_msg or "minor:" in commit_msg:
                bump_type = "minor"
            elif "fix:" in commit_msg or "patch:" in commit_msg:
                bump_type = "patch"
        
        # Create release
        release_info = git_version_manager.create_release(bump_type)
        
        if release_info:
            logger.info(f"Auto-versioned: {bump_type} bump to {release_info['version']}")
        else:
            logger.error("Failed to create release")
        return release_info
        
    except Exception as e:
        logger.error(f"Error in auto-versioning: {e}")
        return None


def get_version_summary() -> Dict[str, str]:
    """Mendapatkan ringkasan versi."""
    try:
        version_info = version_manager.get_version_info()
        git_info = git_version_manager.get_git_info()
        
        return {
            **version_info,
            **git_info
        }
    except Exception as e:
        logger.error(f"Error getting version summary: {e}")
        return {} 