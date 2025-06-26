"""
Build setup handler for AWS Lambda runtime.

This module defines the `BuildSetup` class, a specialized generator that constructs
the import statements and setup invocation logic required to initialize services
in AWS Lambda environments using Bisslog metadata.
"""

from bisslog_schema.setup.runtime_type import RuntimeType
from bisslog_schema.setup.setup_metadata import BisslogSetup

from ..aws_handler_gen_response import AWSHandlerGenResponse
from ..aws_handler_generator import AWSHandlerGenerator


class BuildSetup(AWSHandlerGenerator):
    """
    Generates AWS Lambda setup code from Bisslog configuration.

    This class creates the Python lines necessary to invoke the service setup
    function defined in a `BisslogSetup` object, targeting the AWS Lambda
    runtime. It supports both general setup functions and runtime-specific ones.

    Inherits
    --------
    AWSHandlerGenerator
        Base class for handler code generation utilities.
    """

    def __call__(self, bisslog_setup: BisslogSetup):
        """
        Generates setup code and imports for the AWS Lambda runtime.

        Parameters
        ----------
        bisslog_setup : BisslogSetup
            The metadata definition containing the setup function or
            runtime-specific initialization function.

        Returns
        -------
        AWSHandlerGenResponse or None
            The generated setup code and import dictionary wrapped in a response object.
            Returns None if no valid setup function is found.

        Raises
        ------
        RuntimeError
            If the setup function declares an invalid number of parameters.
        """
        imports = {}
        if bisslog_setup is None:
            return None

        if bisslog_setup.setup_function is not None:
            setup_func = bisslog_setup.setup_function
            imports[setup_func.module] = [setup_func.function_name]

            if setup_func.n_params == 0:
                prebuild_lines = [f"{setup_func.function_name}()"]
            elif setup_func.n_params == 1:
                prebuild_lines = [f"{setup_func.function_name}('{RuntimeType.LAMBDA.value}')"]
            elif setup_func.n_params > 1:
                prebuild_lines = [f"{setup_func.function_name}('{RuntimeType.LAMBDA.value}')  # TODO: change this"]
            else:
                raise RuntimeError(f"Invalid number of parameters for setup function: {setup_func.n_params}")
        else:
            runtime_setup = bisslog_setup.runtime.get(RuntimeType.LAMBDA.value)
            if runtime_setup is None:
                return None
            imports[runtime_setup.module] = [runtime_setup.function_name]
            prebuild_lines = [f"{runtime_setup.module}()"]

        return AWSHandlerGenResponse(build="\n".join(prebuild_lines), importing=imports)
