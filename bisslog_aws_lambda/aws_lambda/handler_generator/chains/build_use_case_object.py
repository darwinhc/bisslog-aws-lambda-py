from typing import Tuple, List

from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfoObject, \
    UseCaseCodeInfoClass

from ..aws_handler_generator import AWSHandlerGenerator
from ..aws_handler_gen_response import AWSHandlerGenResponse

class BuildUseCaseObject(AWSHandlerGenerator):

    def __call__(self, use_case_code_info):

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

