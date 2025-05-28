"""
Module for managing the generation and resolution of AWS Lambda handler code.

This module defines a manager that coordinates the process of reading use case metadata,
generating handler code, and resolving the result through a customizable
strategy (e.g., printing or saving).
"""
from typing import Callable, Optional, Any

from bisslog_schema import read_full_service_metadata
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo

from .handler_generator.handler_generator import generate_handler
from .save_lambda_handler_resolver import save_lambda_handler_default


def default_resolver(___, use_case_code_info: UseCaseCodeInfo, handler_str: str, *_, **__):
    """
    Default resolver that prints the generated handler to the console.

    Parameters
    ----------
    ___ : ServiceInfo
        Full service metadata object.
    use_case_code_info : UseCaseCodeInfo
        Metadata for the specific use case being processed.
    handler_str : str
        Generated handler code.

    Returns
    -------
    str
        Success message.
    """
    print(f"Handler for {use_case_code_info.name}:\n{'-' * 20}\n{handler_str}\n{'-' * 20}")

    return "Successfully processed"


class LambdaHandlerGeneratorManager:
    """
    Manages the end-to-end generation and resolution of AWS Lambda handler code.

    This manager loads service metadata, generates handler code for each use case,
    and delegates the output to a custom resolver (e.g., print to console, save to file).

    Parameters
    ----------
    resolver : Callable[..., Any], optional
        Function that processes the generated handler string. Default prints it.
    generate_handler_resolver : Callable[..., str], optional
        Function that generates handler code given the service and use case info.
    """

    def __init__(self, resolver: Optional[Callable[..., Any]] = None,
                 generate_handler_resolver: Optional[Callable[..., str]] = None):
        self.resolver = resolver or default_resolver
        self.generate_handler = generate_handler_resolver

    def __call__(
            self, *args, metadata_file: Optional[str] = None,
            use_cases_folder_path: Optional[str] = None, filter_uc: Optional[str] = None,
            encoding: str = "utf-8", **kwargs):
        """
        Loads metadata, generates handler code for each use case, and applies the resolver.

        Parameters
        ----------
        metadata_file : str, optional
            Path to the metadata file (YAML/JSON).
        use_cases_folder_path : str, optional
            Directory where use case code is located.
        filter_uc : str, optional
            String to filter which use cases to generate handlers for (by substring match).
        encoding : str, optional
            File encoding for reading metadata (default: "utf-8").
        args : Any
            Additional positional arguments passed to the resolver.
        kwargs : Any
            Additional keyword arguments passed to the resolver.
        """
        full_service_metadata = read_full_service_metadata(
            metadata_file=metadata_file, use_cases_folder_path=use_cases_folder_path,
            encoding=encoding
        )
        service_info = full_service_metadata.declared_metadata
        use_cases = full_service_metadata.discovered_use_cases

        if filter_uc:
            use_cases = {k: v for k, v in use_cases.items() if filter_uc in k}

        for use_case_keyname, use_case_code_info in use_cases.items():
            handler_str = self.generate_handler(service_info, use_case_code_info)
            print(f"{'-' * 20}\nHandler for {use_case_keyname}")
            res = self.resolver(service_info, use_case_code_info, handler_str, *args, **kwargs)
            print(f"Resolver result for {use_case_keyname}: {res}")

def builder_lambda_handler_generator_manager(x):
    """Factory function to create a LambdaHandlerGeneratorManager with a specific resolver."""
    return LambdaHandlerGeneratorManager(x, generate_handler)

lambda_handler_generator_manager_printer = builder_lambda_handler_generator_manager(None)
lambda_handler_generator_manager_saver = builder_lambda_handler_generator_manager(
    save_lambda_handler_default)
