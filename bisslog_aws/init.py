"""
bisslog-aws-py - AWS Integration for bisslog-aws

Provides seamless deployment of bisslog-aws use cases to AWS infrastructure.
"""

import os
from typing import Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path
import tempfile
import zipfile

import boto3
from bisslog_schema import read_service_metadata
from bisslog_schema.use_case_info import UseCaseInfo

from bisslog_aws.use_case_package import UseCasePackage

# Configuration
DEFAULT_USE_CASE_MODULE = "use_cases"
LAMBDA_HANDLER_TEMPLATE = """
from {module_path} import USE_CASE

def handler(event, context):
    return USE_CASE.execute(event)
"""


@dataclass
class AWSDeploymentConfig:
    """Centralized AWS deployment configuration"""
    service_name: str
    env: str = "dev"
    memory_size: int = 128
    timeout: int = 30
    role_arn: str = os.getenv("AWS_LAMBDA_ROLE_ARN")
    vpc_config: Optional[Dict] = None
    layers: Optional[List[str]] = None


class LambdaPackager:
    """Handles Lambda deployment package creation"""

    @staticmethod
    def create_package(handler_code: str, include_modules: List[str] = None) -> str:
        """
        Creates a deployment package zip
        Args:
            handler_code: Lambda handler code
            include_modules: Additional modules to include
        Returns:
            Path to the zip file
        """
        include_modules = include_modules or []

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write handler
            (tmp_path / "handler.py").write_text(handler_code)

            # Add use cases modules
            for module in include_modules:
                # Implementation would copy the module files
                pass

            # Create zip
            zip_path = tmp_path.parent / "lambda_package.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in tmp_path.glob('**/*'):
                    if file.is_file():
                        arcname = file.relative_to(tmp_path)
                        zipf.write(file, arcname)

            return str(zip_path)


class AWSLambdaDeployer:
    """Main deployment orchestrator"""

    def __init__(self, config: AWSDeploymentConfig):
        self.config = config
        self.lambda_client = boto3.client('lambda')

    def deploy_use_case(self, use_case_info: UseCaseInfo):
        """Deploys a single use case to AWS Lambda"""
        # Prepare package
        use_case_pkg = UseCasePackage(use_case_info.keyname)
        package = LambdaPackager.create_package(
            handler_code=use_case_pkg.get_handler_code(),
            include_modules=[f"{DEFAULT_USE_CASE_MODULE}.{use_case_info.keyname}"]
        )

        # Deploy to Lambda
        function_name = f"{self.config.service_name}-{use_case_info.keyname}-{self.config.env}"

        lambda_config = {
            'FunctionName': function_name,
            'Runtime': 'python3.9',
            'Role': self.config.role_arn,
            'Handler': 'handler.handler',
            'MemorySize': self.config.memory_size,
            'Timeout': self.config.timeout,
            'Environment': {
                'Variables': {
                    'SERVICE_NAME': self.config.service_name,
                    'USE_CASE_NAME': use_case_info.keyname,
                    'ENV': self.config.env
                }
            }
        }

        if self.config.vpc_config:
            lambda_config['VpcConfig'] = self.config.vpc_config
        if self.config.layers:
            lambda_config['Layers'] = self.config.layers

        # Implementation would upload the package and configure triggers
        print(f"Ready to deploy {function_name}")


def deploy_service(service_yaml_path: str, config: AWSDeploymentConfig):
    """Main deployment entry point"""
    service_info = read_service_metadata(service_yaml_path)
    deployer = AWSLambdaDeployer(config)

    for use_case_name, use_case in service_info.use_cases.items():
        deployer.deploy_use_case(use_case)

        # TODO: Configure triggers based on use_cases.triggers
        # (API Gateway, EventBridge, SQS, etc.)


# Example usage
if __name__ == "__main__":
    deployment_config = AWSDeploymentConfig(
        service_name="user-service",
        env="prod",
        memory_size=256,
        role_arn="arn:aws:iam::123456789012:role/lambda-role",
        layers=[
            "arn:aws:lambda:us-east-1:123456789012:layer:common-dependencies:1"
        ]
    )

    deploy_service("service.yaml", deployment_config)
