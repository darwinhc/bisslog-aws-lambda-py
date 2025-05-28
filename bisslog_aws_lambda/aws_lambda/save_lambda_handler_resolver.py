"""
Module for resolving and saving AWS Lambda handler files.

This module defines abstract and concrete classes to resolve Lambda handler
strings and persist them to disk. It supports configurable folder structure,
automatic `__init__.py` file creation, and safety checks against absolute paths.
"""

import os
from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional

from bisslog_schema.schema import ServiceInfo
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo


class LambdaHandlerResolver:
    """
    Abstract base class for resolving a Lambda handler string.

    This class defines the interface for resolvers that take a generated
    Lambda handler string and perform a custom action with it (e.g., save it, print it).

    Methods
    -------
    _find_target_folder() -> str
        Determines the default target folder path using environment variables.
    __call__(service_info, use_case_code_info, handler_str)
        Abstract method to resolve the handler string.
    """

    @staticmethod
    def _find_target_folder() -> str:
        """
        Determines the target folder to save the handler file based on environment variables.

        Returns
        -------
        str
            The resolved path to the target folder.
        """
        folder_frameworks = os.getenv("BISSLOG_FOLDER_FRAMEWORKS") or "framework"
        folder_lambda = os.getenv("BISSLOG_FOLDER_LAMBDA") or "lambda_aws"
        return os.path.join(folder_frameworks, folder_lambda)

    @abstractmethod
    def __call__(self, service_info: ServiceInfo,
                 use_case_code_info: UseCaseCodeInfo,
                 handler_str: str) -> Any:
        """
        Resolves the given handler string.

        Parameters
        ----------
        service_info : ServiceInfo
            The service metadata.
        use_case_code_info : UseCaseCodeInfo
            The code information of the use case.
        handler_str : str
            The generated Lambda handler code.

        Returns
        -------
        Any
            The result of the resolver operation.

        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """
        raise NotImplementedError  # pragma: no cover


class SaveLambdaHandlerResolver(LambdaHandlerResolver):
    """
    Resolver that saves the Lambda handler string to a Python file on disk.

    The handler file will be saved in a folder structure with `__init__.py` files
    to ensure valid Python packages.
    """

    def __call__(self, service_info: ServiceInfo,
                 use_case_code_info: UseCaseCodeInfo,
                 handler_str: str, *,
                 target_folder: Optional[str] = None,
                 overwrite: bool = False) -> str:
        """
        Saves the handler string to a file named after the use case.

        Parameters
        ----------
        service_info : ServiceInfo
            The service metadata.
        use_case_code_info : UseCaseCodeInfo
            The code information of the use case.
        handler_str : str
            The generated handler code to save.
        target_folder : str, optional
            Relative path where the handler file should be saved.
            If not provided, the folder is resolved using environment variables.
        overwrite : bool, optional
            Whether to overwrite the file if it already exists. Default is False.

        Returns
        -------
        str
            A message indicating where the handler was saved.

        Raises
        ------
        ValueError
            If `target_folder` is an absolute path.
        """
        if target_folder:
            path = Path(target_folder)
            if path.is_absolute():
                raise ValueError(
                    "Absolute paths are not allowed for target_folder. Use a relative path instead."
                )
        else:
            path = Path(self._find_target_folder())

        self._ensure_folder_with_init(path)

        filename = f"{use_case_code_info.name}_handler.py"
        path_file = os.path.join(path, filename)
        if overwrite or not os.path.isfile(path_file):
            with open(path_file, "w", encoding="utf-8") as f:
                f.write(handler_str)

        return f"Handler saved to {filename}"

    @staticmethod
    def _ensure_folder_with_init(path: Path) -> None:
        """
        Ensures that all folders in the path exist and contain `__init__.py`.

        This is necessary to make sure the generated folders are valid Python packages.

        Parameters
        ----------
        path : Path
            The target folder path where the handler will be saved.
        """
        current = Path()
        for part in path.parts:
            current = current / part
            current.mkdir(exist_ok=True)
            init_file = current / "__init__.py"
            if not init_file.exists():
                init_file.touch()


save_lambda_handler_default = SaveLambdaHandlerResolver()
