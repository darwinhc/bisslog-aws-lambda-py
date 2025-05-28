"""
Module for packaging AWS Lambda deployment artifacts.

This module defines a class responsible for generating `.zip` packages
for AWS Lambda functions by bundling Python source files and a specified
handler file, renaming it to `lambda_function.py` for deployment compatibility.
"""
import os
import tempfile
import zipfile
from pathlib import Path
from shutil import move
from typing import Optional, List, Union


class LambdaAWSPackager:
    """
    AWS Lambda packager for Python projects.

    This class automates the creation of `.zip` deployment packages for
    AWS Lambda functions. It includes Python source files from specified
    folders and inserts a given handler file as `lambda_function.py`.
    """

    def __call__(
            self,
            handler_name: str = None,
            src_folders: Union[str, List[str]] = "src",
            handlers_folder: str = "framework/lambda_aws",
            zip_name: Optional[str] = None
    ) -> List[str]:
        """
        Builds one or more Lambda deployment packages.

        If `handler_name` is specified, creates a single zip file for that handler.
        If `handler_name` is None, generates one zip per `.py` file in `handlers_folder`.

        Parameters
        ----------
        handler_name : str, optional
            Name of the handler file (without `.py`) to package.
        src_folders : Union[str, List[str]], optional
            Folders containing Python source files to include (default is "src").
        handlers_folder : str, optional
            Directory where handler files are located (default is "framework/lambda_aws").
        zip_name : str, optional
            Custom name for the output zip file. Ignored in batch mode.

        Returns
        -------
        List[str]
            List of absolute paths to the generated zip files.

        Raises
        ------
        FileNotFoundError
            If a handler file or a source folder is missing.
        """

        if handler_name is None:
            res = []
            for handler_py_module_name in os.listdir(handlers_folder):
                if handler_py_module_name.endswith(".py"):
                    zip_file = self.generate_zip_file(
                        handler_py_module_name[:-3],
                        zip_name=zip_name,
                        src_folders=src_folders,
                        handlers_folder=handlers_folder)
                    res.append(zip_file)
            return res
        return [self.generate_zip_file(handler_name=handler_name, src_folders=src_folders,
                                       handlers_folder=handlers_folder, zip_name=zip_name)]

    def generate_zip_file(
            self,
            handler_name: str,
            src_folders: Union[str, List[str]] = "src",
            handlers_folder: str = "framework/lambda_aws",
            zip_name: Optional[str] = None
    ) -> str:
        """
        Builds a deployment package for AWS Lambda.

        Parameters
        ----------
        handler_name : str
            Name of the handler file (without `.py`) located in `handlers_folder`.
        src_folders : Union[str, List[str]], optional
            One or more folders containing `.py` files (default is "src").
        handlers_folder : str, optional
            Folder containing handler files (default is "framework/lambda_aws").
        zip_name : str, optional
            Output zip filename (defaults to "{handler_name}.zip").

        Returns
        -------
        str
            Absolute path to the generated zip file.
        """
        handler_file = self._resolve_handler(handler_name, handlers_folder)
        src_folders = self._resolve_src_paths(src_folders, handlers_folder)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            lambda_file = tmpdir_path / "lambda_function.py"
            lambda_file.write_text(handler_file.read_text(encoding="utf-8"), encoding="utf-8")

            zip_output = tmpdir_path / (zip_name or f"{handler_name}.zip")
            with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for src_path in src_folders:
                    for py_file in src_path.rglob("*.py"):
                        rel_path = py_file.relative_to(src_path.parent)
                        zipf.write(py_file, arcname=rel_path)
                zipf.write(lambda_file, arcname="lambda_function.py")

            # Move zip to the current working directory
            final_zip = Path.cwd() / zip_output.name
            move(str(zip_output), str(final_zip))
            return str(final_zip)

    @staticmethod
    def _resolve_handler(handler_name: str, handlers_folder: str) -> Path:
        """
        Resolves the full path to a handler file and checks its existence.

        Parameters
        ----------
        handler_name : str
            Name of the handler (without `.py`).
        handlers_folder : str
            Path to the folder containing handler files.

        Returns
        -------
        Path
            Resolved path to the handler file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """

        handler_path = Path(handlers_folder).resolve() / f"{handler_name}.py"
        if not handler_path.is_file():
            raise FileNotFoundError(f"Handler not found: {handler_path}")
        return handler_path

    @staticmethod
    def _resolve_src_paths(src_folders: Union[str, List[str]], handlers_folder: str) -> set[Path]:
        """
        Resolves and validates source folders to include in the zip.

        Parameters
        ----------
        src_folders : Union[str, List[str]]
            One or more directories containing Python source files.
        handlers_folder : str
            Folder containing the handler file (will be excluded if present).

        Returns
        -------
        set of Path
            A set of valid, resolved paths to source folders.

        Raises
        ------
        FileNotFoundError
            If any of the specified folders do not exist.
        """

        if isinstance(src_folders, str):
            src_folders = [src_folders]
        handlers_path = Path(handlers_folder).resolve()
        paths = set()
        for folder in src_folders:
            path_obj = Path(folder).resolve()
            if path_obj == handlers_path:
                continue
            if not path_obj.exists():
                raise FileNotFoundError(f"Source folder not found: {folder}")
            paths.add(path_obj)
        return paths


lambda_aws_packager = LambdaAWSPackager()
