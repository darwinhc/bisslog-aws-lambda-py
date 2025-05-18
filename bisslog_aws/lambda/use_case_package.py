

import importlib
from typing import Optional, List

from bisslog import UseCaseBase
from bisslog_schema.use_case_info import UseCaseInfo

from bisslog_aws.constants import LAMBDA_HANDLER_TEMPLATE
from bisslog_aws.utils.to_snake_case import to_snake_case

DEFAULT_USE_CASE_VAR_NAME = "USE_CASE"
DEFAULT_USE_CASE_MODULE = "use_cases"

class UseCasePackage:
    """Represents a use case package structure"""

    def __init__(self, use_case: UseCaseInfo, module_path: Optional[str] = None,
                 var_name_in_module : Optional[str] = None):
        self.use_case_info = use_case
        self.module_path = module_path or DEFAULT_USE_CASE_MODULE
        self._validate_and_search_info(var_name_in_module or DEFAULT_USE_CASE_VAR_NAME)
        self._var_name_in_module = None
        self._class_use_case = None

    def _validate_and_search_info(self, suggested_var_name: str = None) -> Optional[str]:
        """Validates the use case module structure"""
        try:
            module = importlib.import_module(f"{self.module_path}.{self.use_case_info.keyname}")
            if hasattr(module, suggested_var_name):
                self._var_name_in_module = suggested_var_name
            if hasattr(module, self.use_case_info.keyname):
                self._var_name_in_module = self.use_case_info.keyname
            if hasattr(module, self.use_case_info.keyname.capitalize()):
                self._var_name_in_module = self.use_case_info.keyname.capitalize()

            snake_case_uc_name = to_snake_case(self.use_case_info.keyname)
            if hasattr(module, snake_case_uc_name):
                self._var_name_in_module = snake_case_uc_name
            if hasattr(module, snake_case_uc_name.upper()):
                self._var_name_in_module = snake_case_uc_name.upper()

            vars_module = vars(module)
            for key, value in vars_module.items():
                if isinstance(value, UseCaseBase):
                    self._var_name_in_module = key
            class_use_case = self._find_class_use_case(module)
            if class_use_case:
                self._class_use_case = class_use_case
            raise ValueError("UseCase obj not found in "
                             f"{self.module_path}.{self.use_case_info.keyname}")
        except ImportError as e:
            raise ImportError(f"Use case module {self.module_path}."
                              f"{self.use_case_info.keyname} not found") from e

    @staticmethod
    def _find_class_use_case(use_case_keyname: str, module) -> Optional[str]:
        """Find a class that is a subclass of UseCaseBase
        and whose name matches the use case keyname.

        Parameters
        ----------
        use_case_keyname : str
            Key name of a use case
        module: Module
            Python module to find a class for

        Returns
        -------
        str, optional
            Class name key"""
        for key, value in vars(module).items():
            if not isinstance(value, type) or not issubclass(value, UseCaseBase):
                continue
            if (use_case_keyname.lower().replace("_", "")
                    .startswith(key.lower().replace("_", ""))):
                return key
        return None

    def get_handler_code(self) -> str:
        """Generates Lambda handler code"""

        try:
            module = importlib.import_module(f"{self.module_path}.{self.use_case_info.keyname}")
        except ImportError as e:
            raise ImportError(f"Use case module {self.module_path}."
                              f"{self.use_case_info.keyname} not found") from e
        lines = []
        if self._var_name_in_module is None:
            class_use_case = self._find_class_use_case(self.use_case_info.keyname, module)

        else:
            lines.append(f"from {self.module_path} import {self._var_name_in_module}")


        return LAMBDA_HANDLER_TEMPLATE.format(
            module_path=f"{self.module_path}.{self.use_case_info.keyname}"
        )
