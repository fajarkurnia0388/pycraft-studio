"""
Tujuan: Generator template proyek Python standar
Dependensi: dataclasses, typing
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: generator = ProjectTemplateGenerator().get_available_templates()
"""

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TemplateConfig:
    """Konfigurasi template proyek."""

    name: str
    description: str
    dependencies: List[str]
    entry_point: str
    additional_files: List[str]
    build_config: Dict[str, str]


class ProjectTemplateGenerator:
    """Generator template proyek Python standar."""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, TemplateConfig]:
        """Inisialisasi template yang tersedia."""
        return {
            "console": TemplateConfig(
                name="Console Application",
                description="Aplikasi command line sederhana",
                dependencies=["click>=8.0.0"],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={"console": "True", "onefile": "True", "name": "app"},
            ),
            "gui": TemplateConfig(
                name="GUI Application",
                description="Aplikasi GUI dengan tkinter",
                dependencies=["tkinter"],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={"console": "False", "onefile": "True", "name": "app"},
            ),
            "web": TemplateConfig(
                name="Web Application",
                description="Aplikasi web dengan Flask",
                dependencies=["flask>=2.0.0", "gunicorn>=20.0.0"],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={"console": "True", "onefile": "True", "name": "webapp"},
            ),
            "api": TemplateConfig(
                name="API Application",
                description="API dengan FastAPI",
                dependencies=["fastapi>=0.68.0", "uvicorn>=0.15.0"],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={"console": "True", "onefile": "True", "name": "api"},
            ),
            "microservice": TemplateConfig(
                name="Microservice",
                description="Microservice dengan FastAPI dan Docker",
                dependencies=["fastapi>=0.68.0", "uvicorn>=0.15.0", "docker>=6.0.0"],
                entry_point="src/main.py",
                additional_files=[
                    "requirements.txt",
                    "README.md",
                    ".gitignore",
                    "Dockerfile",
                    "docker-compose.yml",
                ],
                build_config={
                    "console": "True",
                    "onefile": "True",
                    "name": "microservice",
                },
            ),
            "data_science": TemplateConfig(
                name="Data Science Project",
                description="Project data science dengan Jupyter dan pandas",
                dependencies=[
                    "pandas>=1.3.0",
                    "numpy>=1.21.0",
                    "matplotlib>=3.4.0",
                    "jupyter>=1.0.0",
                ],
                entry_point="src/main.py",
                additional_files=[
                    "requirements.txt",
                    "README.md",
                    ".gitignore",
                    "notebooks/",
                ],
                build_config={"console": "True", "onefile": "True", "name": "data_app"},
            ),
            "automation": TemplateConfig(
                name="Automation Script",
                description="Script otomatisasi dengan scheduling",
                dependencies=["schedule>=1.1.0", "requests>=2.25.0"],
                entry_point="src/main.py",
                additional_files=[
                    "requirements.txt",
                    "README.md",
                    ".gitignore",
                    "config/",
                ],
                build_config={
                    "console": "True",
                    "onefile": "True",
                    "name": "automation",
                },
            ),
            "desktop_modern": TemplateConfig(
                name="Modern Desktop App",
                description="Aplikasi desktop modern dengan PyQt6",
                dependencies=["PyQt6>=6.0.0"],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={
                    "console": "False",
                    "onefile": "True",
                    "name": "desktop_app",
                },
            ),
            "cli_argparse": TemplateConfig(
                name="CLI Argparse Application",
                description="Aplikasi command line dengan argparse",
                dependencies=[],
                entry_point="src/main.py",
                additional_files=["requirements.txt", "README.md", ".gitignore"],
                build_config={"console": "True", "onefile": "True", "name": "cli_app"},
            ),
        }

    def get_available_templates(self) -> List[str]:
        """Mendapatkan daftar template yang tersedia."""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Optional[TemplateConfig]:
        """Mendapatkan informasi template."""
        return self.templates.get(template_name)

    def create_project(
        self, project_name: str, template_name: str, output_path: str
    ) -> bool:
        """
        Membuat proyek baru berdasarkan template.

        Args:
            project_name: Nama proyek.
            template_name: Jenis template.
            output_path: Path untuk output proyek.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            template = self.templates.get(template_name)
            if not template:
                logger.error(f"Template tidak ditemukan: {template_name}")
                return False

            project_path = Path(output_path) / project_name
            if project_path.exists():
                logger.error(f"Direktori sudah ada: {project_path}")
                return False

            # Buat struktur direktori
            self._create_directory_structure(project_path)

            # Buat file-file template
            self._create_template_files(project_path, project_name, template)

            logger.info(f"Proyek berhasil dibuat: {project_path}")
            return True

        except Exception as e:
            logger.error(f"Error saat membuat proyek: {e}")
            return False

    def _create_directory_structure(self, project_path: Path):
        """Membuat struktur direktori proyek."""
        directories = ["src", "tests", "resources", "docs", "config"]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
            (project_path / directory / "__init__.py").touch()

    def _create_template_files(
        self, project_path: Path, project_name: str, template: TemplateConfig
    ):
        """Membuat file-file template."""

        # Main entry point
        main_content = self._get_main_template(template.name.lower())
        (project_path / "src" / "main.py").write_text(main_content)

        # Requirements.txt
        requirements_content = self._get_requirements_template(template.dependencies)
        (project_path / "requirements.txt").write_text(requirements_content)

        # README.md
        readme_content = self._get_readme_template(project_name, template)
        (project_path / "README.md").write_text(readme_content)

        # .gitignore
        gitignore_content = self._get_gitignore_template()
        (project_path / ".gitignore").write_text(gitignore_content)

        # Build config
        build_config_content = self._get_build_config_template(template.build_config)
        (project_path / "build_config.py").write_text(build_config_content)

    def _get_main_template(self, template_type: str) -> str:
        """Mendapatkan template main.py berdasarkan jenis."""
        templates = {
            "console": '''"""
{project_name} - Console Application

Entry point untuk aplikasi console.
"""

import click


@click.command()
@click.option('--name', default='World', help='Nama untuk disapa')
def main(name):
    """Aplikasi console sederhana."""
    click.echo(f"Hello, {name}!")


if __name__ == "__main__":
    main()
''',
            "gui": '''"""
{project_name} - GUI Application

Entry point untuk aplikasi GUI.
"""

import tkinter as tk
from tkinter import messagebox


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("{project_name}")
        self.root.geometry("400x300")

        # Widget
        self.label = tk.Label(root, text="Hello, World!")
        self.label.pack(pady=20)

        self.button = tk.Button(root, text="Click Me!", command=self.show_message)
        self.button.pack(pady=10)

    def show_message(self):
        messagebox.showinfo("Info", "Button clicked!")


def main():
    """Main function."""
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
''',
            "web": '''"""
{project_name} - Web Application

Entry point untuk aplikasi web Flask.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """Halaman utama."""
    return render_template('index.html')


@app.route('/api/hello')
def hello():
    """API endpoint."""
    return {{"message": "Hello, World!"}}


def main():
    """Main function."""
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
''',
            "api": '''"""
{project_name} - API Application

Entry point untuk aplikasi API FastAPI.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{project_name}", version="1.0.0")


class Message(BaseModel):
    text: str


@app.get("/")
def read_root():
    """Root endpoint."""
    return {{"message": "Hello World"}}


@app.get("/items/{{item_id}}")
def read_item(item_id: int, q: str = None):
    """Get item endpoint."""
    return {{"item_id": item_id, "q": q}}


@app.post("/message")
def create_message(message: Message):
    """Create message endpoint."""
    return {{"message": message.text}}


def main():
    """Main function."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
''',
            "microservice": '''"""
{project_name} - Microservice

Entry point untuk microservice dengan FastAPI dan Docker.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{project_name}", version="1.0.0")


class ServiceRequest(BaseModel):
    data: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{project_name}"}}


@app.get("/")
def read_root():
    """Root endpoint."""
    return {{"message": "Microservice is running"}}


@app.post("/process")
def process_data(request: ServiceRequest):
    """Process data endpoint."""
    try:
        # Process the data here
        result = f"Processed: {{request.data}}"
        logger.info(f"Processed data: {{request.data}}")
        return {{"result": result, "status": "success"}}
    except Exception as e:
        logger.error(f"Error processing data: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main function."""
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
''',
            "data_science": '''"""
{project_name} - Data Science Project

Entry point untuk project data science.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(file_path: str = "data/sample.csv"):
    """Load sample data."""
    try:
        # Create sample data if file doesn't exist
        data = pd.DataFrame({{
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        }})
        data.to_csv(file_path, index=False)
        logger.info(f"Created sample data: {{file_path}}")
        return data
    except Exception as e:
        logger.error(f"Error loading data: {{e}}")
        return None


def analyze_data(data: pd.DataFrame):
    """Analyze the data."""
    if data is None:
        return

    print("=== Data Analysis ===")
    print(f"Shape: {{data.shape}}")
    print(f"Columns: {{list(data.columns)}}")
    print("\\nSummary Statistics:")
    print(data.describe())

    # Create visualization
    plt.figure(figsize=(10, 6))
    data.plot.scatter(x='x', y='y', c='category', colormap='viridis')
    plt.title('Data Visualization')
    plt.savefig('output/visualization.png')
    plt.close()

    logger.info("Analysis completed")


def main():
    """Main function."""
    print("Starting Data Science Project...")

    # Load data
    data = load_data()

    # Analyze data
    analyze_data(data)

    print("Data Science project completed!")


if __name__ == "__main__":
    main()
''',
            "automation": '''"""
{project_name} - Automation Script

Entry point untuk script otomatisasi dengan scheduling.
"""

import schedule
import time
import requests
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def sample_task():
    """Sample automation task."""
    try:
        logger.info("Running automation task...")

        # Example: Check a website
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            logger.info("Task completed successfully")
        else:
            logger.warning(f"Task failed with status: {{response.status_code}}")

    except Exception as e:
        logger.error(f"Error in automation task: {{e}}")


def load_config():
    """Load configuration."""
    try:
        with open('config/settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config
        config = {{
            "schedule_interval": 60,  # seconds
            "max_retries": 3,
            "log_level": "INFO"
        }}
        with open('config/settings.json', 'w') as f:
            json.dump(config, f, indent=2)
        return config


def main():
    """Main function."""
    logger.info("Starting automation script...")

    # Load configuration
    config = load_config()

    # Schedule tasks
    schedule.every(config["schedule_interval"]).seconds.do(sample_task)

    # Run initial task
    sample_task()

    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Automation script stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {{e}}")
            time.sleep(5)


if __name__ == "__main__":
    main()
''',
            "desktop_modern": '''"""
{project_name} - Modern Desktop Application

Entry point untuk aplikasi desktop modern dengan PyQt6.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{project_name}")
        self.setGeometry(100, 100, 600, 400)

        # Set modern style
        self.setStyleSheet("""
            QMainWindow {{
                background-color: #f0f0f0;
            }}
            QPushButton {{
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #106ebe;
            }}
            QLabel {{
                font-size: 16px;
                color: #333;
            }}
        """)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Add widgets
        title_label = QLabel("Welcome to {project_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title_label)

        info_label = QLabel("This is a modern desktop application built with PyQt6")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        button = QPushButton("Click Me!")
        button.clicked.connect(self.show_message)
        layout.addWidget(button)

        # Add spacing
        layout.addStretch()

    def show_message(self):
        """Show a message when button is clicked."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Info", "Button clicked! This is a modern desktop app.")


def main():
    """Main function."""
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
''',
            "cli_argparse": (
                "import argparse\n\n"
                "def main():\n"
                '    parser = argparse.ArgumentParser(description="Aplikasi CLI dengan argparse")\n'
                '    parser.add_argument("--name", default="World", help="Nama untuk disapa")\n'
                "    args = parser.parse_args()\n"
                '    print(f"Hello, {args.name}!")\n\n'
                'if __name__ == "__main__":\n'
                "    main()\n"
            ),
        }

        return templates.get(template_type, templates["console"])

    def _get_requirements_template(self, dependencies: List[str]) -> str:
        """Mendapatkan template requirements.txt."""
        content = "# Dependencies\n"
        for dep in dependencies:
            content += f"{dep}\n"
        content += "\n# Development dependencies\n"
        content += "pytest>=6.0.0\n"
        content += "black>=21.0.0\n"
        content += "flake8>=3.8.0\n"
        return content

    def _get_readme_template(self, project_name: str, template: TemplateConfig) -> str:
        """Mendapatkan template README.md."""
        return f"""# {project_name}

{template.description}

## Instalasi

```bash
pip install -r requirements.txt
```

## Penggunaan

```bash
python src/main.py
```

## Build dengan PyInstaller

```bash
python build_config.py
```

## Testing

```bash
pytest tests/
```

## Struktur Proyek

```
{project_name}/
├── src/           # Kode sumber
├── tests/         # Unit tests
├── resources/     # Asset
├── docs/          # Dokumentasi
└── config/        # Konfigurasi
```
"""

    def _get_gitignore_template(self) -> str:
        """Mendapatkan template .gitignore."""
        return """# Byte-compiled / optimized / DLL files
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

    def _get_build_config_template(self, build_config: Dict[str, str]) -> str:
        """Mendapatkan template build_config.py."""
        return f'''"""
Build configuration untuk PyInstaller.

Auto-generated oleh PyCraft Studio.
"""

import PyInstaller.__main__
import os


def build_app():
    """Build aplikasi dengan PyInstaller."""
    PyInstaller.__main__.run([
        'src/main.py',
        '--onefile',
        '--console={build_config.get("console", "True")}',
        '--name={build_config.get("name", "app")}',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
    ])


if __name__ == "__main__":
    build_app()
'''
