"""
Tujuan: Batch processing untuk membangun multiple file Python
Dependensi: src.core.builder, src.utils.file_utils
Tanggal Pembuatan: 24 Juni 2025
Penulis: Tim Pengembangan
Contoh: batch = BatchBuilder().build_multiple(["file1.py", "file2.py"], "exe")
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..utils.file_utils import FileManager, FileValidator
from .builder import BuildResult, BuildStatus, ProjectBuilder

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Data class untuk hasil batch build."""

    total_files: int
    successful_builds: int
    failed_builds: int
    results: Dict[str, BuildResult]
    total_time: float
    status: str


class BatchBuilder:
    """
    Builder untuk batch processing multiple file Python.

    Menangani build multiple file secara paralel dengan
    progress tracking dan error handling.
    """

    def __init__(self, output_directory: Optional[str] = None, max_workers: int = 3):
        """
        Inisialisasi BatchBuilder.

        Args:
            output_directory: Direktori output untuk hasil build.
            max_workers: Jumlah worker thread maksimal untuk paralel processing.
        """
        self.output_directory = output_directory or "output"
        self.max_workers = max_workers
        self.builder = ProjectBuilder(self.output_directory)

        # Ensure output directory exists
        FileManager.ensure_directory_exists(self.output_directory)

    def build_multiple(
        self,
        python_files: List[str],
        output_format: str,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> BatchResult:
        """
        Membangun multiple file Python secara paralel.

        Args:
            python_files: List path ke file Python yang akan di-build.
            output_format: Format output (exe, app, binary).
            progress_callback: Callback untuk progress tracking.

        Returns:
            BatchResult berisi hasil batch build.
        """
        start_time = time.time()

        # Validate input files
        valid_files = self._validate_files(python_files)
        if not valid_files:
            return BatchResult(
                total_files=len(python_files),
                successful_builds=0,
                failed_builds=len(python_files),
                results={},
                total_time=time.time() - start_time,
                status="No valid files found",
            )

        logger.info(f"Starting batch build for {len(valid_files)} files")

        # Build files in parallel
        results = {}
        successful_builds = 0
        failed_builds = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all build tasks
            future_to_file = {
                executor.submit(
                    self._build_single_file, file_path, output_format
                ): file_path
                for file_path in valid_files
            }

            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_file)):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results[file_path] = result

                    if result.success:
                        successful_builds += 1
                        logger.info(f"Build successful: {file_path}")
                    else:
                        failed_builds += 1
                        logger.error(
                            f"Build failed: {file_path} - {result.error_message}"
                        )

                    # Call progress callback
                    if progress_callback:
                        progress_callback(file_path, i + 1, len(valid_files))

                except Exception as e:
                    failed_builds += 1
                    logger.error(f"Exception during build of {file_path}: {e}")
                    results[file_path] = BuildResult(
                        success=False,
                        output_path=None,
                        error_message=str(e),
                        build_time=0,
                        status=BuildStatus.FAILED,
                        log_output="",
                    )

        total_time = time.time() - start_time
        status = (
            "completed"
            if failed_builds == 0
            else f"completed with {failed_builds} failures"
        )

        logger.info(f"Batch build {status} in {total_time:.2f} seconds")

        return BatchResult(
            total_files=len(python_files),
            successful_builds=successful_builds,
            failed_builds=failed_builds,
            results=results,
            total_time=total_time,
            status=status,
        )

    def _validate_files(self, python_files: List[str]) -> List[str]:
        """
        Memvalidasi list file Python.

        Args:
            python_files: List path ke file Python.

        Returns:
            List berisi path file yang valid.
        """
        valid_files = []

        for file_path in python_files:
            if FileValidator.is_valid_python_file(file_path):
                valid_files.append(file_path)
            else:
                logger.warning(f"Invalid Python file: {file_path}")

        return valid_files

    def _build_single_file(self, file_path: str, output_format: str) -> BuildResult:
        """
        Membangun single file Python.

        Args:
            file_path: Path ke file Python.
            output_format: Format output.

        Returns:
            BuildResult berisi hasil build.
        """
        try:
            return self.builder.build(file_path, output_format)
        except Exception as e:
            logger.error(f"Error building {file_path}: {e}")
            return BuildResult(
                success=False,
                output_path=None,
                error_message=str(e),
                build_time=0,
                status=BuildStatus.FAILED,
                log_output="",
            )

    def build_from_directory(
        self,
        directory_path: str,
        output_format: str,
        recursive: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> BatchResult:
        """
        Membangun semua file Python dalam direktori.

        Args:
            directory_path: Path ke direktori.
            output_format: Format output.
            recursive: Apakah mencari file secara recursive.
            progress_callback: Callback untuk progress tracking.

        Returns:
            BatchResult berisi hasil batch build.
        """
        # Find all Python files in directory
        if recursive:
            python_files = FileManager.list_python_files(directory_path)
        else:
            # Only files in root directory
            dir_path = Path(directory_path)
            python_files = [
                str(f)
                for f in dir_path.glob("*.py")
                if FileValidator.is_valid_python_file(str(f))
            ]

        if not python_files:
            logger.warning(f"No Python files found in {directory_path}")
            return BatchResult(
                total_files=0,
                successful_builds=0,
                failed_builds=0,
                results={},
                total_time=0,
                status="No Python files found",
            )

        logger.info(f"Found {len(python_files)} Python files in {directory_path}")

        return self.build_multiple(python_files, output_format, progress_callback)

    def get_build_summary(self, batch_result: BatchResult) -> str:
        """
        Mendapatkan summary dari hasil batch build.

        Args:
            batch_result: Hasil batch build.

        Returns:
            String berisi summary build.
        """
        summary = f"""
Batch Build Summary:
===================
Total Files: {batch_result.total_files}
Successful: {batch_result.successful_builds}
Failed: {batch_result.failed_builds}
Total Time: {batch_result.total_time:.2f} seconds
Status: {batch_result.status}

Success Rate: {(batch_result.successful_builds / batch_result.total_files * 100):.1f}%
        """

        if batch_result.failed_builds > 0:
            summary += "\nFailed Builds:\n"
            for file_path, result in batch_result.results.items():
                if not result.success:
                    summary += f"  - {file_path}: {result.error_message}\n"

        return summary.strip()
