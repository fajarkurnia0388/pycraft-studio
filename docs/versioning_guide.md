# Auto-Versioning & Changelog Guide

## Overview

PyCraft Studio dilengkapi dengan sistem auto-versioning dan changelog generator yang otomatis untuk manajemen versi yang konsisten dan dokumentasi perubahan yang terstruktur.

## Fitur Utama

### 1. Semantic Versioning
- **Major**: Breaking changes (x.0.0)
- **Minor**: New features (0.x.0)
- **Patch**: Bug fixes (0.0.x)

### 2. Auto-Versioning dari Commit Messages
- Analisis otomatis commit messages
- Bump version berdasarkan konvensi
- Integration dengan Git workflow

### 3. Changelog Generator
- Generate changelog otomatis
- Kategorisasi perubahan
- Format yang konsisten

## Penggunaan

### Basic Version Management

```python
from src.utils.versioning import version_manager, changelog_generator

# Dapatkan versi saat ini
current_version = version_manager.current_version
print(f"Current version: {current_version}")

# Bump version
new_version = version_manager.bump_version("patch")  # 1.2.3 -> 1.2.4
new_version = version_manager.bump_version("minor")  # 1.2.3 -> 1.3.0
new_version = version_manager.bump_version("major")  # 1.2.3 -> 2.0.0
```

### Changelog Management

```python
from src.utils.versioning import changelog_generator

# Tambah perubahan
changelog_generator.add_change("added", "New feature", "John Doe")
changelog_generator.add_change("fixed", "Bug fix", "Jane Smith")
changelog_generator.add_change("changed", "Improvement", "Bob Wilson")

# Generate changelog
changelog = changelog_generator.generate_changelog("1.2.3", "2025-06-24")
print(changelog)

# Save ke file
changelog_generator.save_changelog("1.2.3", "2025-06-24")
```

### Git Integration

```python
from src.utils.versioning import git_version_manager

# Dapatkan info Git
git_info = git_version_manager.get_git_info()
print(f"Branch: {git_info['branch']}")
print(f"Commit: {git_info['commit_hash']}")

# Buat release
release_info = git_version_manager.create_release(
    bump_type="patch",
    release_notes="Bug fixes and improvements"
)
print(f"New version: {release_info['version']}")
```

### Auto-Versioning dari Commits

```python
from src.utils.versioning import auto_version_from_commits

# Auto-version berdasarkan commit messages
release_info = auto_version_from_commits()
if release_info:
    print(f"Auto-versioned to: {release_info['version']}")
```

## Commit Message Conventions

### Conventional Commits
```bash
# Patch (bug fix)
git commit -m "fix: resolve memory leak in build process"

# Minor (new feature)
git commit -m "feat: add support for multiple output formats"

# Major (breaking change)
git commit -m "feat!: change API interface for better performance"
git commit -m "BREAKING CHANGE: remove deprecated build method"
```

### Auto-Versioning Rules
- `fix:` → Patch bump
- `feat:` → Minor bump
- `BREAKING CHANGE:` → Major bump
- `major:` → Major bump
- `minor:` → Minor bump
- `patch:` → Patch bump

## File Structure

```
project/
├── VERSION              # Current version
├── CHANGELOG.md         # Generated changelog
├── .git/                # Git repository
└── src/utils/versioning.py  # Versioning module
```

## Workflow Integration

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check conventional commits
commit_msg=$(cat "$1")
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"; then
    echo "Error: Commit message must follow conventional commits format"
    exit 1
fi
```

### Post-commit Hook
```bash
#!/bin/bash
# .git/hooks/post-commit

# Auto-version if needed
python -c "
from src.utils.versioning import auto_version_from_commits
auto_version_from_commits()
"
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Auto Versioning
on:
  push:
    branches: [main]

jobs:
  version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Auto Version
        run: |
          pip install -r requirements.txt
          python -c "
          from src.utils.versioning import auto_version_from_commits
          result = auto_version_from_commits()
          if result:
              print(f'::set-output name=version::{result[\"version\"]}')
          "
        id: version
      
      - name: Create Release
        if: steps.version.outputs.version
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ steps.version.outputs.version }}
          release_name: Release v${{ steps.version.outputs.version }}
          body: |
            Auto-generated release
            
            See CHANGELOG.md for details
          draft: false
          prerelease: false
```

## Best Practices

### 1. Commit Message Guidelines
- Gunakan conventional commits format
- Jelaskan perubahan dengan jelas
- Referensi issue jika ada

### 2. Version Management
- Bump version sebelum release
- Gunakan semantic versioning
- Dokumentasi breaking changes

### 3. Changelog Maintenance
- Update changelog untuk setiap perubahan
- Kategorisasi yang konsisten
- Include author information

### 4. Release Process
```bash
# 1. Update changelog
changelog_generator.add_change("added", "New feature", "Developer")

# 2. Bump version
version_manager.bump_version("minor")

# 3. Commit changes
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 1.3.0"

# 4. Create tag
git tag -a v1.3.0 -m "Release v1.3.0"

# 5. Push
git push origin main --tags
```

## Troubleshooting

### Common Issues

1. **Version File Not Found**
   ```python
   # Create default version file
   version_manager = VersionManager("VERSION")
   # Will create VERSION file with "0.1.0"
   ```

2. **Git Not Available**
   ```python
   # Handle gracefully
   git_info = git_version_manager.get_git_info()
   if not git_info:
       print("Git information not available")
   ```

3. **Invalid Version Format**
   ```python
   # Ensure semantic versioning
   try:
       version_manager.bump_version("invalid")
   except ValueError:
       print("Invalid bump type")
   ```

### Version Migration

Untuk proyek yang sudah ada:

```python
# 1. Initialize version manager
version_manager = VersionManager("VERSION")

# 2. Set current version
version_manager._save_version("1.0.0")

# 3. Generate initial changelog
changelog_generator.save_changelog("1.0.0", "2025-06-24")
```

## Advanced Features

### Custom Version Schemes
```python
class CustomVersionManager(VersionManager):
    def bump_version(self, bump_type: str) -> str:
        # Custom versioning logic
        pass
```

### Multiple Changelog Formats
```python
# Generate different formats
changelog_md = changelog_generator.generate_changelog("1.2.3")
changelog_json = changelog_generator.generate_changelog_json("1.2.3")
```

### Integration dengan Package Managers
```python
# Update setup.py
def update_setup_py_version(version):
    with open("setup.py", "r") as f:
        content = f.read()
    
    content = re.sub(
        r'version="[^"]*"',
        f'version="{version}"',
        content
    )
    
    with open("setup.py", "w") as f:
        f.write(content)
```

## Kesimpulan

Auto-versioning dan changelog generator membantu:
- Manajemen versi yang konsisten
- Dokumentasi perubahan yang terstruktur
- Otomatisasi release process
- Tracking perubahan yang akurat

Gunakan fitur-fitur ini untuk streamline development workflow dan maintain project history yang baik. 