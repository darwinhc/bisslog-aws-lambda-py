"""
Module for orchestrating the generation of complete AWS Lambda handler code.

This module defines a class that coordinates multiple generator components to
produce a fully functional Lambda handler for a given use case based on its triggers.
"""
from typing import Callable

from bisslog_schema.schema import ServiceInfo
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo

from .aws_handler_gen_response import AWSHandlerGenResponse
from .chains.build_use_case_object import BuildUseCaseObject
from .chains.default_error_handler_generator import DefaultHandlerGenerator
from .chains.manager_trigger_handler_generator import ManagerTriggerHandlerGenerator


class HandlerGenerator:
    """
    Coordinates the generation of complete AWS Lambda handler code.

    This class integrates multiple generator components:
    - Builds the use case object.
    - Generates trigger-specific dispatch logic.
    - Appends a fallback error handler.

    Parameters
    ----------
    manager_trigger_gen : Callable[..., AWSHandlerGenResponse]
        Generator responsible for building code for each trigger.
    build_use_case_obj_gen : Callable[..., AWSHandlerGenResponse]
        Generator that constructs the use case object.
    default_handler_gen : Callable[..., AWSHandlerGenResponse]
        Generator that provides a fallback error handler.
    """

    def __init__(self, manager_trigger_gen: Callable[..., AWSHandlerGenResponse],
                 build_use_case_obj_gen: Callable[..., AWSHandlerGenResponse],
                 default_handler_gen: Callable[..., AWSHandlerGenResponse]):
        self._manager_trigger_gen = manager_trigger_gen
        self._build_use_case_obj_gen = build_use_case_obj_gen
        self._default_handler_gen = default_handler_gen

    def __call__(self, service_info: ServiceInfo, use_case_code_info: UseCaseCodeInfo) -> str:
        """
        Generates full handler code for a given use case based on its trigger metadata.

        Parameters
        ----------
        service_info : ServiceInfo
            Metadata of the service including all use cases and their triggers.
        use_case_code_info : UseCaseCodeInfo
            Static code metadata for the specific use case.

        Returns
        -------
        str
            The complete AWS Lambda handler code as a string.

        Raises
        ------
        RuntimeError
            If required metadata is missing.
        ValueError
            If the `BuildUseCaseObject` generator fails to produce a `var_name`.
        """
        if service_info is None or use_case_code_info is None:
            raise RuntimeError("service_info and use_case_code_info cannot be None")
        use_case_keyname = use_case_code_info.name
        use_case_metadata = service_info.use_cases[use_case_keyname]

        triggers = use_case_metadata.triggers

        res = AWSHandlerGenResponse(importing={"bisslog.utils.mapping": {"Mapper"}})

        res_build_use_obj = self._build_use_case_obj_gen(use_case_code_info)
        res += res_build_use_obj
        if not isinstance(res_build_use_obj.extra, dict) \
                or "var_name" not in res_build_use_obj.extra:
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
