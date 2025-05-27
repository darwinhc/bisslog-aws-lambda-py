from typing import Dict, List, Callable, Set

from bisslog_schema.schema import ServiceInfo
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo, \
    UseCaseCodeInfoObject, UseCaseCodeInfoClass


from .aws_handler_gen_response import AWSHandlerGenResponse
from .chains.build_use_case_object import BuildUseCaseObject
from .chains.default_error_handler_generator import DefaultHandlerGenerator
from .chains.manager_trigger_handler_generator import ManagerTriggerHandlerGenerator


class HandlerGenerator:

    def __init__(self, manager_trigger_gen: Callable[..., AWSHandlerGenResponse],
                 build_use_case_obj_gen: Callable[..., AWSHandlerGenResponse],
                 default_handler_gen: Callable[..., AWSHandlerGenResponse]):
        self._manager_trigger_gen = manager_trigger_gen
        self._build_use_case_obj_gen = build_use_case_obj_gen
        self._default_handler_gen = default_handler_gen


    @staticmethod
    def _generate_imports_string(imports: Dict[str, Set[str]]):
        return "\n".join(f"from {source} import {', '.join(var)}" if var else f"import {source}"
                  for source, var in imports.items())

    def __call__(self, service_info: ServiceInfo, use_case_code_info: UseCaseCodeInfo) -> str:
        if service_info is None or use_case_code_info is None:
            raise RuntimeError(f"service_info and use_case_code_info cannot be None")
        use_case_keyname = use_case_code_info.name
        use_case_metadata = service_info.use_cases[use_case_keyname]

        triggers = use_case_metadata.triggers

        res = AWSHandlerGenResponse(importing={"bisslog.utils.mapping": {"Mapper"}})

        res_build_use_obj = self._build_use_case_obj_gen(use_case_code_info)
        res += res_build_use_obj
        if res_build_use_obj.extra and "var_name" not in res_build_use_obj.extra:
            raise ValueError(
                "This execution was expected to generate 'var_name', internal Bisslog issue.")

        # Variable name
        var_name = res_build_use_obj.extra["var_name"]


        res += self._manager_trigger_gen(triggers, var_name)
        res += self._default_handler_gen()

        return res.generate_handler_code()


generate_handler = HandlerGenerator(
    ManagerTriggerHandlerGenerator(),
    BuildUseCaseObject(),
    DefaultHandlerGenerator()
)
