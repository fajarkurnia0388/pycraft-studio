"""
Enhanced Main Window untuk PyCraft Studio.

GUI dengan fitur-fitur canggih untuk project management.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser
from pathlib import Path
import threading
import logging

from ..core.enhanced_builder import EnhancedProjectBuilder
from ..core.config import ConfigManager
from ..utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class EnhancedMainWindow:
    """Enhanced main window dengan fitur project management."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyCraft Studio - Enhanced")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.builder = EnhancedProjectBuilder()
        
        # Initialize theme manager
        theme = self.config_manager.get_config("theme", "light")
        self.theme_manager = ThemeManager(self.root, theme=theme)
        
        # List widget yang perlu diubah warna manual
        self.themable_widgets = []
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        
        # Apply theme to all widgets after UI is complete
        self.root.after(100, self.update_widget_themes)  # Small delay to ensure widgets are rendered
        
        # Status variables
        self.current_project_path = None
        self.build_thread = None
        
    def setup_ui(self):
        """Setup user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_build_tab()
        self.create_project_tab()
        self.create_analysis_tab()
        self.create_validation_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        # Tambahkan status bar ke themable_widgets
        self.themable_widgets.append(self.status_bar)
        
    def create_build_tab(self):
        """Create build tab."""
        build_frame = ttk.Frame(self.notebook)
        self.notebook.add(build_frame, text="Build")
        
        # File selection
        file_frame = ttk.LabelFrame(build_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(file_frame, text="Python File:").grid(row=0, column=0, sticky=tk.W)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)
        
        # Build options
        options_frame = ttk.LabelFrame(build_frame, text="Build Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="binary")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, 
                                   values=["exe", "app", "binary"], state="readonly")
        format_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(options_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W)
        self.output_dir_var = tk.StringVar(value="output")
        ttk.Entry(options_frame, textvariable=self.output_dir_var, width=40).grid(row=1, column=1, padx=5, sticky=tk.W)
        ttk.Button(options_frame, text="Browse", command=self.browse_output_dir).grid(row=1, column=2)
        
        # Build buttons
        button_frame = ttk.Frame(build_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.build_button = ttk.Button(button_frame, text="Build", command=self.start_build)
        self.build_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_build, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Progress
        progress_frame = ttk.LabelFrame(build_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Log output
        log_frame = ttk.LabelFrame(build_frame, text="Build Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # Tambahkan log_text ke themable_widgets
        self.themable_widgets.append(self.log_text)
        
    def create_project_tab(self):
        """Create project template tab."""
        project_frame = ttk.Frame(self.notebook)
        self.notebook.add(project_frame, text="Project Templates")
        
        # Template selection
        template_frame = ttk.LabelFrame(project_frame, text="Create New Project", padding=10)
        template_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(template_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W)
        self.project_name_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.project_name_var, width=30).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(template_frame, text="Template:").grid(row=1, column=0, sticky=tk.W)
        self.template_var = tk.StringVar()
        templates = self.builder.get_available_templates()
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                     values=templates, state="readonly")
        template_combo.grid(row=1, column=1, padx=5, sticky=tk.W)
        template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        ttk.Label(template_frame, text="Output Path:").grid(row=2, column=0, sticky=tk.W)
        self.project_path_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.project_path_var, width=50).grid(row=2, column=1, padx=5, sticky=tk.W)
        ttk.Button(template_frame, text="Browse", command=self.browse_project_path).grid(row=2, column=2)
        
        # Template info
        info_frame = ttk.LabelFrame(project_frame, text="Template Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.template_info_text = scrolledtext.ScrolledText(info_frame, height=8)
        self.template_info_text.pack(fill=tk.BOTH, expand=True)
        self.themable_widgets.append(self.template_info_text)
        
        # Create button
        button_frame = ttk.Frame(project_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_project_button = ttk.Button(button_frame, text="Create Project", 
                                               command=self.create_project)
        self.create_project_button.pack(side=tk.LEFT, padx=5)
        
    def create_analysis_tab(self):
        """Create dependency analysis tab."""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Dependency Analysis")
        
        # Project selection
        project_frame = ttk.LabelFrame(analysis_frame, text="Project Analysis", padding=10)
        project_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(project_frame, text="Project Path:").grid(row=0, column=0, sticky=tk.W)
        self.analysis_path_var = tk.StringVar()
        ttk.Entry(project_frame, textvariable=self.analysis_path_var, width=50).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Button(project_frame, text="Browse", command=self.browse_analysis_path).grid(row=0, column=2)
        
        # Analysis buttons
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Analyze Project", command=self.analyze_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Requirements", command=self.generate_requirements).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Validate Dependencies", command=self.validate_dependencies).pack(side=tk.LEFT, padx=5)
        
        # Analysis results
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.analysis_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        self.themable_widgets.append(self.analysis_text)
        
    def create_validation_tab(self):
        """Create project validation tab."""
        validation_frame = ttk.Frame(self.notebook)
        self.notebook.add(validation_frame, text="Project Validation")
        
        # Project selection
        project_frame = ttk.LabelFrame(validation_frame, text="Project Validation", padding=10)
        project_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(project_frame, text="Project Path:").grid(row=0, column=0, sticky=tk.W)
        self.validation_path_var = tk.StringVar()
        ttk.Entry(project_frame, textvariable=self.validation_path_var, width=50).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Button(project_frame, text="Browse", command=self.browse_validation_path).grid(row=0, column=2)
        
        # Validation buttons
        button_frame = ttk.Frame(validation_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Validate Structure", command=self.validate_structure).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fix Structure", command=self.fix_structure).pack(side=tk.LEFT, padx=5)
        
        # Validation results
        results_frame = ttk.LabelFrame(validation_frame, text="Validation Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.validation_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.validation_text.pack(fill=tk.BOTH, expand=True)
        self.themable_widgets.append(self.validation_text)
        
    def create_settings_tab(self):
        """Create settings tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings
        config_frame = ttk.LabelFrame(settings_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Default output directory
        ttk.Label(config_frame, text="Default Output Directory:").grid(row=0, column=0, sticky=tk.W)
        self.default_output_var = tk.StringVar(value=self.config_manager.get_config("default_output_dir", "output"))
        ttk.Entry(config_frame, textvariable=self.default_output_var, width=40).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Button(config_frame, text="Browse", command=self.browse_default_output).grid(row=0, column=2)
        
        # Auto validation
        self.auto_validation_var = tk.BooleanVar(value=self.config_manager.get_config("auto_validation", True))
        ttk.Checkbutton(config_frame, text="Auto validation before build", 
                       variable=self.auto_validation_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Theme
        ttk.Label(config_frame, text="Theme:").grid(row=2, column=0, sticky=tk.W)
        self.theme_var = tk.StringVar(value=self.config_manager.get_config("theme", "light"))
        self.theme_combo = ttk.Combobox(config_frame, textvariable=self.theme_var, 
                                   values=self.theme_manager.get_available_themes(), state="readonly")
        self.theme_combo.grid(row=2, column=1, padx=5, sticky=tk.W)
        self.theme_combo.bind('<<ComboboxSelected>>', self.on_theme_selected)
        ttk.Button(config_frame, text="Add Theme", command=self.add_theme_dialog).grid(row=2, column=2, padx=5)
        
        # Theme color settings
        self.colors_frame = ttk.LabelFrame(settings_frame, text="Theme Colors", padding=10)
        self.colors_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.color_vars = {}
        color_labels = [
            ("Background", "background"),
            ("Foreground", "foreground"),
            ("Button BG", "button_bg"),
            ("Button FG", "button_fg"),
            ("Accent", "accent")
        ]
        for i, (label, key) in enumerate(color_labels):
            ttk.Label(self.colors_frame, text=label+":").grid(row=i//2, column=(i%2)*3, sticky=tk.W)
            var = tk.StringVar()
            self.color_vars[key] = var
            entry = ttk.Entry(self.colors_frame, textvariable=var, width=12)
            entry.grid(row=i//2, column=(i%2)*3+1, padx=5, sticky=tk.W)
            btn = ttk.Button(self.colors_frame, text="Pilih", command=lambda k=key: self.choose_color(k))
            btn.grid(row=i//2, column=(i%2)*3+2, padx=2)
        
        # Action buttons
        self.apply_btn = ttk.Button(self.colors_frame, text="Apply", command=self.apply_theme_colors)
        self.apply_btn.grid(row=3, column=0, pady=5)
        self.reset_btn = ttk.Button(self.colors_frame, text="Reset", command=self.reset_theme)
        self.reset_btn.grid(row=3, column=1, pady=5)
        self.delete_btn = ttk.Button(self.colors_frame, text="Delete", command=self.delete_theme)
        self.delete_btn.grid(row=3, column=2, pady=5)
        self.set_default_btn = ttk.Button(self.colors_frame, text="Set as Default", command=self.set_as_default_theme)
        self.set_default_btn.grid(row=3, column=3, pady=5)
        
        self.update_theme_color_inputs()
        self.update_theme_action_buttons()
        
        # Save button
        ttk.Button(config_frame, text="Save Settings", command=self.save_settings).grid(row=4, column=0, pady=10)

    def update_theme_color_inputs(self):
        theme = self.theme_var.get()
        style = self.theme_manager.get_style_dict(theme)
        for key, var in self.color_vars.items():
            var.set(style.get(key, ""))

    def update_theme_action_buttons(self):
        theme = self.theme_var.get()
        is_default = theme in self.theme_manager.DEFAULT_THEMES
        is_custom = theme in self.theme_manager.custom_themes
        self.reset_btn.config(state=tk.NORMAL if is_default else tk.DISABLED)
        self.delete_btn.config(state=tk.NORMAL if is_custom else tk.DISABLED)
        self.set_default_btn.config(state=tk.NORMAL if is_default else tk.DISABLED)

    def on_theme_selected(self, event=None):
        theme = self.theme_var.get()
        self.update_theme_color_inputs()
        self.update_theme_action_buttons()
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()

    def choose_color(self, key):
        color = colorchooser.askcolor(title=f"Pilih {key.capitalize()}", initialcolor=self.color_vars[key].get())
        if color[1]:
            self.color_vars[key].set(color[1])

    def apply_theme_colors(self):
        theme = self.theme_var.get()
        style = {k: v.get() for k, v in self.color_vars.items()}
        self.theme_manager.set_theme_colors(theme, style)
        # Persist custom themes
        self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()
        messagebox.showinfo("Success", f"Theme '{theme}' updated.")

    def reset_theme(self):
        theme = self.theme_var.get()
        self.theme_manager.reset_theme(theme)
        self.update_theme_color_inputs()
        self.theme_manager.apply_theme(theme)
        self.update_widget_themes()
        messagebox.showinfo("Reset", f"Theme '{theme}' reset to default.")

    def delete_theme(self):
        theme = self.theme_var.get()
        if theme in self.theme_manager.custom_themes:
            if messagebox.askyesno("Delete Theme", f"Delete custom theme '{theme}'?"):
                self.theme_manager.delete_custom_theme(theme)
                self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
                # Update dropdown
                self.theme_combo["values"] = self.theme_manager.get_available_themes()
                self.theme_var.set("light")
                self.on_theme_selected()

    def add_theme_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Theme")
        dialog.geometry("300x200")
        ttk.Label(dialog, text="Theme Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)
        color_vars = {}
        color_labels = [
            ("Background", "background", "#282c34"),
            ("Foreground", "foreground", "#abb2bf"),
            ("Button BG", "button_bg", "#3c4048"),
            ("Button FG", "button_fg", "#abb2bf"),
            ("Accent", "accent", "#e06c75")
        ]
        for label, key, default in color_labels:
            ttk.Label(dialog, text=label+":").pack()
            var = tk.StringVar(value=default)
            color_vars[key] = var
            row = ttk.Frame(dialog)
            row.pack()
            ttk.Entry(row, textvariable=var, width=12).pack(side=tk.LEFT)
            ttk.Button(row, text="Pilih", command=lambda k=key: self._choose_color_dialog(color_vars, k)).pack(side=tk.LEFT)
        def on_add():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Theme name required", parent=dialog)
                return
            if name in self.theme_manager.get_available_themes():
                messagebox.showerror("Error", "Theme name already exists", parent=dialog)
                return
            style = {k: v.get() for k, v in color_vars.items()}
            self.theme_manager.add_custom_theme(name, style)
            self.config_manager.set_custom_themes(self.theme_manager.custom_themes)
            self.theme_combo["values"] = self.theme_manager.get_available_themes()
            self.theme_var.set(name)
            self.on_theme_selected()
            dialog.destroy()
        ttk.Button(dialog, text="Add", command=on_add).pack(pady=10)

    def _choose_color_dialog(self, color_vars, key):
        color = colorchooser.askcolor(title=f"Pilih {key.capitalize()}", initialcolor=color_vars[key].get())
        if color[1]:
            color_vars[key].set(color[1])
        
    def setup_menu(self):
        """Setup menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Report", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Project Analysis", command=lambda: self.notebook.select(2))
        tools_menu.add_command(label="Project Validation", command=lambda: self.notebook.select(3))
        tools_menu.add_command(label="Project Templates", command=lambda: self.notebook.select(1))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    # Event handlers
    def browse_file(self):
        """Browse for Python file."""
        filename = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.current_project_path = str(Path(filename).parent)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_project_path(self):
        """Browse for project path."""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.project_path_var.set(directory)
    
    def browse_analysis_path(self):
        """Browse for analysis path."""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.analysis_path_var.set(directory)
    
    def browse_validation_path(self):
        """Browse for validation path."""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.validation_path_var.set(directory)
    
    def browse_default_output(self):
        """Browse for default output directory."""
        directory = filedialog.askdirectory(title="Select Default Output Directory")
        if directory:
            self.default_output_var.set(directory)
    
    def on_template_selected(self, event):
        """Handle template selection."""
        template_name = self.template_var.get()
        if template_name:
            template_info = self.builder.get_template_info(template_name)
            if template_info:
                info_text = f"""Template: {template_info.name}
Description: {template_info.description}
Entry Point: {template_info.entry_point}
Dependencies: {', '.join(template_info.dependencies)}
Additional Files: {', '.join(template_info.additional_files)}
"""
                self.template_info_text.delete(1.0, tk.END)
                self.template_info_text.insert(1.0, info_text)
    
    def create_project(self):
        """Create new project from template."""
        project_name = self.project_name_var.get().strip()
        template_name = self.template_var.get()
        output_path = self.project_path_var.get().strip()
        
        if not all([project_name, template_name, output_path]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            result = self.builder.create_project_from_template(
                project_name, template_name, output_path
            )
            
            if result["success"]:
                messagebox.showinfo("Success", f"Project created successfully!\nPath: {result['project_path']}")
                self.analysis_path_var.set(result['project_path'])
                self.validation_path_var.set(result['project_path'])
            else:
                messagebox.showerror("Error", result.get("error", "Unknown error"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}")
    
    def start_build(self):
        """Start build process."""
        file_path = self.file_path_var.get().strip()
        output_format = self.format_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a Python file")
            return
        
        # Check if auto validation is enabled
        if self.auto_validation_var.get():
            self.start_build_with_validation(file_path, output_format)
        else:
            self.start_normal_build(file_path, output_format)
    
    def start_build_with_validation(self, file_path: str, output_format: str):
        """Start build with validation."""
        self.build_thread = threading.Thread(
            target=self._build_with_validation_thread,
            args=(file_path, output_format)
        )
        self.build_thread.start()
        
        self.build_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Building with validation...")
    
    def start_normal_build(self, file_path: str, output_format: str):
        """Start normal build."""
        self.build_thread = threading.Thread(
            target=self._build_thread,
            args=(file_path, output_format)
        )
        self.build_thread.start()
        
        self.build_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Building...")
    
    def _build_with_validation_thread(self, file_path: str, output_format: str):
        """Build thread with validation."""
        try:
            project_path = str(Path(file_path).parent)
            result = self.builder.build_with_validation(project_path, output_format)
            
            self.root.after(0, self._build_completed, result)
            
        except Exception as e:
            self.root.after(0, self._build_error, str(e))
    
    def _build_thread(self, file_path: str, output_format: str):
        """Normal build thread."""
        try:
            result = self.builder.build(file_path, output_format)
            self.root.after(0, self._build_completed, result)
            
        except Exception as e:
            self.root.after(0, self._build_error, str(e))
    
    def _build_completed(self, result):
        """Handle build completion."""
        self.progress_bar.stop()
        self.build_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        
        if result.success:
            self.progress_var.set(f"Build completed successfully in {result.build_time:.2f}s")
            self.log_text.insert(tk.END, f"\nBuild successful!\nOutput: {result.output_path}\n")
            messagebox.showinfo("Success", f"Build completed!\nOutput: {result.output_path}")
        else:
            self.progress_var.set("Build failed")
            self.log_text.insert(tk.END, f"\nBuild failed: {result.error_message}\n")
            messagebox.showerror("Error", f"Build failed: {result.error_message}")
        
        # Add log output
        if result.log_output:
            self.log_text.insert(tk.END, f"\n{result.log_output}\n")
    
    def _build_error(self, error: str):
        """Handle build error."""
        self.progress_bar.stop()
        self.build_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_var.set("Build failed")
        self.log_text.insert(tk.END, f"\nError: {error}\n")
        messagebox.showerror("Error", f"Build error: {error}")
    
    def cancel_build(self):
        """Cancel build process."""
        if self.builder.cancel_build():
            self.progress_bar.stop()
            self.build_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.progress_var.set("Build cancelled")
            self.log_text.insert(tk.END, "\nBuild cancelled by user\n")
    
    def analyze_project(self):
        """Analyze project dependencies."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            analysis = self.builder.analyze_project(project_path)
            
            if "error" in analysis:
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(1.0, f"Error: {analysis['error']}")
            else:
                report = self.builder.generate_project_report(project_path)
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(1.0, report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")
    
    def generate_requirements(self):
        """Generate requirements.txt."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            success = self.builder.dependency_analyzer.generate_requirements_txt(project_path)
            if success:
                messagebox.showinfo("Success", "requirements.txt generated successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate requirements.txt")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate requirements: {e}")
    
    def validate_dependencies(self):
        """Validate project dependencies."""
        project_path = self.analysis_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            validation = self.builder.dependency_analyzer.validate_dependencies(project_path)
            
            if validation.get("valid", False):
                messagebox.showinfo("Success", "All dependencies are valid!")
            else:
                missing = validation.get("missing_dependencies", [])
                messagebox.showwarning("Warning", f"Missing dependencies: {', '.join(missing)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")
    
    def validate_structure(self):
        """Validate project structure."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            validation = self.builder.build_validator.validate_project_structure(project_path)
            
            report = self.builder.build_validator.get_validation_report(project_path)
            self.validation_text.delete(1.0, tk.END)
            self.validation_text.insert(1.0, report)
            
            if validation.get("valid", False):
                messagebox.showinfo("Success", "Project structure is valid!")
            else:
                messagebox.showwarning("Warning", "Project structure has issues")
                
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")
    
    def generate_report(self):
        """Generate comprehensive project report."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            report = self.builder.generate_project_report(project_path)
            self.validation_text.delete(1.0, tk.END)
            self.validation_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def fix_structure(self):
        """Fix project structure."""
        project_path = self.validation_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select a project path")
            return
        
        try:
            success = self.builder.build_validator.generate_project_structure(project_path)
            if success:
                messagebox.showinfo("Success", "Project structure fixed!")
                self.validate_structure()  # Refresh validation
            else:
                messagebox.showerror("Error", "Failed to fix project structure")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fix structure: {e}")
    
    def save_settings(self):
        """Save application settings."""
        try:
            self.config_manager.update_config("default_output_dir", self.default_output_var.get())
            self.config_manager.update_config("auto_validation", self.auto_validation_var.get())
            self.config_manager.update_config("theme", self.theme_var.get())
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def open_project(self):
        """Open existing project."""
        directory = filedialog.askdirectory(title="Open Project")
        if directory:
            self.analysis_path_var.set(directory)
            self.validation_path_var.set(directory)
            self.notebook.select(2)  # Switch to analysis tab
    
    def save_report(self):
        """Save current report."""
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Get current tab content
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 2:  # Analysis tab
                    content = self.analysis_text.get(1.0, tk.END)
                elif current_tab == 3:  # Validation tab
                    content = self.validation_text.get(1.0, tk.END)
                else:
                    content = self.log_text.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Success", "Report saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """PyCraft Studio - Enhanced

A Python GUI application for building Python scripts into executables.

Features:
- Project templates
- Dependency analysis
- Project validation
- Enhanced build process
- Comprehensive reporting

Version: 2.0.0
"""
        messagebox.showinfo("About", about_text)
    
    def update_widget_themes(self):
        """Update warna widget non-ttk agar sesuai tema aktif."""
        style_dict = self.theme_manager.get_style_dict(self.theme_manager.get_current_theme())
        for widget in self.themable_widgets:
            try:
                widget.configure(bg=style_dict["background"], fg=style_dict["foreground"])
            except Exception:
                pass
        # Force refresh ttk styles
        self.root.update_idletasks()
    
    def run(self):
        """Run the application."""
        self.root.mainloop() 

    def set_as_default_theme(self):
        theme = self.theme_var.get()
        if theme in self.theme_manager.DEFAULT_THEMES:
            if messagebox.askyesno("Set as Default", f"Yakin ingin mengubah default untuk theme '{theme}'?\nTindakan ini akan mengubah default reset theme."):
                style = {k: v.get() for k, v in self.color_vars.items()}
                self.theme_manager.set_default_theme(theme, style)
                self.config_manager.set_default_theme_overrides(self.theme_manager.default_theme_overrides)
                messagebox.showinfo("Set as Default", f"Default untuk theme '{theme}' berhasil diubah.") 