import os
from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional

from bisslog_schema.schema import ServiceInfo
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo


class LambdaHandlerResolver:
    """
    A class to resolve the handler for a Lambda function based on the provided handler string.
    """

    @staticmethod
    def _find_target_folder():
        folder_frameworks = os.getenv("BISSLOG_FOLDER_FRAMEWORKS")
        folder_frameworks = folder_frameworks or "framework"

        folder_lambda = os.getenv("BISSLOG_FOLDER_LAMBDA")
        folder_lambda = folder_lambda or "lambda_aws"
        return os.path.join(folder_frameworks, folder_lambda)

    @abstractmethod
    def __call__(self, service_info: ServiceInfo,
                 use_case_code_info: UseCaseCodeInfo, handler_str: str) -> Any:

        raise NotImplementedError


class SaveLambdaHandlerResolver(LambdaHandlerResolver):
    """
    A resolver that saves the generated handler string to a file.
    """


    def __call__(self, service_info: ServiceInfo,
                 use_case_code_info: UseCaseCodeInfo, handler_str: str,
                 target_folder: Optional[str] = None, overwrite: bool = False) -> str:
        """
        Saves the handler string to a file named after the use case.
        """
        if target_folder:
            path = Path(target_folder)
            if path.is_absolute():
                raise ValueError("Absolute paths are not allowed for target_folder. Use a relative path instead.")
        else:
            path = Path(self._find_target_folder())

        self._ensure_folder_with_init(path)

        filename = f"{use_case_code_info.name}_handler.py"
        path_file = os.path.join(path, filename)
        if overwrite or not os.path.isfile(path_file):
            with open(path_file, "w") as f:
                f.write(handler_str)

        return f"Handler saved to {filename}"

    @staticmethod
    def _ensure_folder_with_init(path: Path) -> None:
        """
        Ensures the folder structure exists and contains `__init__.py` in each subfolder.

        Parameters
        ----------
        path : Path
            Relative path where the handler file will be saved.
        """
        current = Path()
        for part in path.parts:
            current = current / part
            current.mkdir(exist_ok=True)
            init_file = current / "__init__.py"
            if not init_file.exists():
                init_file.touch()

save_lambda_handler_default = SaveLambdaHandlerResolver()
