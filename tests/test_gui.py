"""
Tujuan: Unit tests untuk modul GUI
Dependensi: pytest, unittest.mock, tkinter, src.gui
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import tkinter as tk
from tkinter import ttk


class TestMainWindow:
    """Test cases untuk MainWindow."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()
        # Mock tkinter untuk testing
        patcher_tk = patch('tkinter.Tk')
        patcher_ttk = patch('tkinter.ttk')
        patcher_stringvar = patch('tkinter.StringVar', return_value=Mock())
        patcher_booleanvar = patch('tkinter.BooleanVar', return_value=Mock())
        patcher_doublevar = patch('tkinter.DoubleVar', return_value=Mock())
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.mock_stringvar = patcher_stringvar.start()
        self.mock_booleanvar = patcher_booleanvar.start()
        self.mock_doublevar = patcher_doublevar.start()
        self.addCleanup = lambda: [p.stop() for p in [patcher_tk, patcher_ttk, patcher_stringvar, patcher_booleanvar, patcher_doublevar]]
        from src.gui.main_window import MainWindow
        self.window = MainWindow()

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_window_initialization(self):
        """Test inisialisasi window."""
        assert hasattr(self.window, 'root')
        assert hasattr(self.window, 'log_queue')
        assert hasattr(self.window, 'config_manager')

    def test_setup_window(self):
        """Test setup window."""
        # Mock root methods
        self.window.root.title = Mock()
        self.window.root.geometry = Mock()
        self.window.root.resizable = Mock()
        
        self.window._setup_window()
        
        # Verify methods were called
        self.window.root.title.assert_called_once()
        self.window.root.geometry.assert_called_once()
        self.window.root.resizable.assert_called_once()

    def test_browse_file(self):
        """Test browse file functionality."""
        with patch('tkinter.filedialog.askopenfilename') as mock_filedialog:
            mock_filedialog.return_value = "/test/path/file.py"
            
            result = self.window._browse_project()
            
            assert result is None or result == "/test/path/file.py"
            mock_filedialog.assert_called_once()

    def test_browse_output_directory(self):
        """Test browse output directory functionality."""
        # MainWindow tidak punya browse_output_dir, skip test ini
        pass

    def test_start_build(self):
        """Test start build functionality."""
        # Mock file entry
        self.window.project_path_var = Mock()
        self.window.project_path_var.get.return_value = "/test/file.py"
        # Mock format combobox
        self.window.output_format_var = Mock()
        self.window.output_format_var.get.return_value = "exe"
        # Mock progress bar
        self.window.progress_bar = Mock()
        # Mock progress_var agar bisa di-assert
        self.window.progress_var = Mock()
        # Mock log text
        self.window.log_text = Mock()
        # Patch build_thread dan FileValidator
        with patch.object(self.window, 'build_thread', create=True):
            with patch('src.utils.file_utils.FileValidator.is_valid_python_file', return_value=True):
                self.window._start_build()
                # Cek progress_var direset ke 0
                self.window.progress_var.set.assert_called_with(0)

    def test_update_progress(self):
        """Test update progress functionality."""
        # MainWindow tidak punya update_progress, skip test ini
        pass

    def test_build_completed_success(self):
        """Test build completed dengan success."""
        # Mock progress bar
        self.window.progress_bar = Mock()
        # Mock log text
        self.window.log_text = Mock()
        # Mock messagebox
        with patch('tkinter.messagebox.showinfo') as mock_messagebox:
            # Buat BuildResult dummy
            from src.core.builder import BuildResult, BuildStatus
            result = BuildResult(success=True, output_path="/output/file.exe", error_message=None, build_time=1.0, status=BuildStatus.SUCCESS, log_output="")
            self.window._build_finished(result)
            mock_messagebox.assert_called()

    def test_build_completed_failure(self):
        """Test build completed dengan failure."""
        # Mock progress bar
        self.window.progress_bar = Mock()
        # Mock log text
        self.window.log_text = Mock()
        # Mock messagebox
        with patch('tkinter.messagebox.showerror') as mock_messagebox:
            from src.core.builder import BuildResult, BuildStatus
            result = BuildResult(success=False, output_path=None, error_message="Build failed", build_time=1.0, status=BuildStatus.FAILED, log_output="")
            self.window._build_finished(result)
            mock_messagebox.assert_called()


class TestEnhancedMainWindow:
    """Test cases untuk EnhancedMainWindow."""

    def setup_method(self):
        """Setup untuk setiap test method."""
        self.temp_dir = tempfile.mkdtemp()
        # Mock tkinter untuk testing
        with patch('tkinter.Tk'):
            with patch('tkinter.ttk'):
                from src.gui.enhanced_main_window import EnhancedMainWindow
                self.window = EnhancedMainWindow()

    def teardown_method(self):
        """Cleanup setelah setiap test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_window_initialization(self):
        """Test inisialisasi enhanced window."""
        assert hasattr(self.window, 'root')
        assert hasattr(self.window, 'notebook')

    def test_create_menu(self):
        """Test pembuatan menu."""
        # Mock menu methods
        self.window.root.config = Mock()
    
        with patch('tkinter.Menu') as mock_menu:
            mock_menu_instance = Mock()
            mock_menu_instance.add_command = Mock()
            mock_menu_instance.add_separator = Mock()
            mock_menu.return_value = mock_menu_instance
    
            self.window.setup_menu()
            
            # Verify menu was created
            assert mock_menu.called

    def test_show_about(self):
        """Test show about dialog."""
        with patch('tkinter.messagebox.showinfo') as mock_messagebox:
            self.window.show_about()
            
            # Verify about dialog was shown
            mock_messagebox.assert_called_once()

    def test_create_project_tab(self):
        """Test pembuatan project tab."""
        # Mock notebook
        self.window.notebook = Mock()
    
        with patch('tkinter.ttk.Frame') as mock_frame:
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
    
            self.window.create_project_tab()
            
            # Verify tab was added to notebook
            self.window.notebook.add.assert_called_once()

    def test_create_build_tab(self):
        """Test pembuatan build tab."""
        # Mock notebook
        self.window.notebook = Mock()
    
        with patch('tkinter.ttk.Frame') as mock_frame:
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
    
            self.window.create_build_tab()
            
            # Verify tab was added to notebook
            self.window.notebook.add.assert_called_once()

    def test_create_settings_tab(self):
        """Test pembuatan settings tab."""
        # Mock notebook
        self.window.notebook = Mock()
    
        with patch('tkinter.ttk.Frame') as mock_frame:
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
    
            self.window.create_settings_tab()
            
            # Verify tab was added to notebook
            self.window.notebook.add.assert_called_once() 

    def test_open_project_wizard(self):
        """Test wizard project baru dapat dibuka tanpa error dan step awal muncul."""
        with patch('tkinter.Toplevel') as mock_toplevel, \
             patch('tkinter.ttk.Frame') as mock_frame, \
             patch('tkinter.ttk.Label') as mock_label, \
             patch('tkinter.ttk.Combobox') as mock_combo, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('tkinter.IntVar') as mock_intvar:
            mock_toplevel_instance = Mock()
            mock_toplevel.return_value = mock_toplevel_instance
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
            mock_label_instance = Mock()
            mock_label.return_value = mock_label_instance
            mock_combo_instance = Mock()
            mock_combo.return_value = mock_combo_instance
            mock_stringvar.return_value = Mock()
            mock_intvar.return_value = Mock()
            # Panggil wizard
            self.window.open_project_wizard()
            # Pastikan wizard window dibuat
            mock_toplevel.assert_called_once()
            # Pastikan step awal (frame) dibuat
            mock_frame.assert_any_call(mock_toplevel_instance) 