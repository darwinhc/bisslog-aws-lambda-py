


LAMBDA_HANDLER_TEMPLATE = """
from {module_path} import {var_name}

def handler(event, context):
    return USE_CASE.execute(event)
"""
