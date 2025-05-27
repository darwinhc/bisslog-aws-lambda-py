from typing import Callable, Optional, Any

from bisslog_schema import read_full_service_metadata
from bisslog_schema.service_metadata_with_code import ServiceInfoWithCode
from bisslog_schema.use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo

from .handler_generator.handler_generator import generate_handler
from .save_lambda_handler_resolver import save_lambda_handler_default


def default_resolver(service_info, use_case_code_info: UseCaseCodeInfo, handler_str: str, *_, **__):
    """
    Default resolver that does nothing.
    This can be overridden to implement custom logic.
    """
    print(f"Handler for {use_case_code_info.name}:\n{'-' * 20}\n{handler_str}\n{'-' * 20}")

    return "Successfully processed"


class LambdaHandlerGeneratorManager:


    def __init__(self, resolver: Optional[Callable[..., Any]] = None,
                 generate_handler_resolver: Optional[Callable[..., str]] = None):
        self.resolver = resolver or default_resolver
        self.generate_handler = generate_handler_resolver


    def __call__(
            self, *args, metadata_file: Optional[str] = None,
            use_cases_folder_path: Optional[str] = None, filter_uc: Optional[str] = None,
            encoding: str = "utf-8", **kwargs):
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
            print(f"{'-'*20}\nHandler for {use_case_keyname}")
            res = self.resolver(service_info, use_case_code_info, handler_str, *args, **kwargs)
            print(f"Resolver result for {use_case_keyname}: {res}")


builder_lambda_handler_generator_manager = lambda x: LambdaHandlerGeneratorManager(x, generate_handler)


lambda_handler_generator_manager_printer = builder_lambda_handler_generator_manager(None)
lambda_handler_generator_manager_saver = builder_lambda_handler_generator_manager(save_lambda_handler_default)
