import os
from abc import abstractmethod
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
                 target_folder: Optional[str] = None) -> str:
        """
        Saves the handler string to a file named after the use case.
        """
        path = target_folder or self._find_target_folder()

        folder_path_split = path.split(os.path.sep)

        buffer = None
        for folder_path_i in folder_path_split:
            if buffer is None:
                buffer = folder_path_i
            else:
                buffer = os.path.join(buffer, folder_path_i)
            if not os.path.exists(buffer):
                os.makedirs(buffer, exist_ok=True)

            init_file_framework_path = os.path.join(buffer, "__init__.py")
            if not os.path.isfile(init_file_framework_path):
                open(init_file_framework_path, "a").close()

        filename = f"{use_case_code_info.name}_handler.py"
        path_file = os.path.join(path, filename)
        if not os.path.isfile(path_file):
            with open(path_file, "w") as f:
                f.write(handler_str)

        return f"Handler saved to {filename}"

save_lambda_handler_default = SaveLambdaHandlerResolver()
