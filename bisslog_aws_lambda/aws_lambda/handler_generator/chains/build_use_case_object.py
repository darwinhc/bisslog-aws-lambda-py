"""
Generator for constructing the use case object in an AWS Lambda handler.

This module defines a class responsible for producing the necessary code
and imports to instantiate or reference a use case object, depending on its representation.
"""

from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfoObject, \
    UseCaseCodeInfoClass

from ..aws_handler_gen_response import AWSHandlerGenResponse
from ..aws_handler_generator import AWSHandlerGenerator


class BuildUseCaseObject(AWSHandlerGenerator):
    """
    Builds the Python code required to instantiate or reference a use case object.

    This generator handles two possible representations:
    - As an already available object (via `UseCaseCodeInfoObject`)
    - As a class to instantiate (via `UseCaseCodeInfoClass`)
    """

    def __call__(self, use_case_code_info):
        """
        Generates import and instantiation code for a given use case.

        Parameters
        ----------
        use_case_code_info : Union[UseCaseCodeInfoObject, UseCaseCodeInfoClass]
            Metadata describing how the use case is represented in code.

        Returns
        -------
        AWSHandlerGenResponse
            A response object containing:
            - Required imports
            - Code to instantiate or reference the use case
            - A `var_name` entry in `extra` for downstream reference

        Raises
        ------
        RuntimeError
            If the provided `use_case_code_info` type is not recognized.
        """
        imports = {}
        prebuild_lines = []
        # find or build variable of use case
        if isinstance(use_case_code_info, UseCaseCodeInfoObject):
            var_name = use_case_code_info.var_name
            imports[use_case_code_info.module] = [var_name]
        elif isinstance(use_case_code_info, UseCaseCodeInfoClass):
            var_name = use_case_code_info.name.upper()
            imports[use_case_code_info.module] = [use_case_code_info.class_name]
            prebuild_lines.append(f"{var_name} = {use_case_code_info.class_name}()")  # simple
        else:
            raise RuntimeError(f"Unknown use case code type {use_case_code_info}")

        return AWSHandlerGenResponse(None, "\n".join(prebuild_lines), imports,
                                     {"var_name": var_name})
