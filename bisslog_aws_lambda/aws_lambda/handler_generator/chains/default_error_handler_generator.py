"""
Fallback handler generator for unmatched AWS Lambda events.

This module defines a generator that provides a default `raise` clause for unrecognized
event formats in a Lambda function.
"""
from typing import Tuple, List

from ..aws_handler_gen_response import AWSHandlerGenResponse
from ..aws_handler_generator import AWSHandlerGenerator


class DefaultHandlerGenerator(AWSHandlerGenerator):
    """
    Generates default fallback logic for unmatched AWS Lambda events.

    This generator is typically appended at the end of a handler to ensure
    unrecognized event payloads raise a meaningful error.
    """

    def __call__(self):
        """
        Produces a default error-raising block for unrecognized events.

        Returns
        -------
        AWSHandlerGenResponse
            Response object with Python code that raises a `RuntimeError`
            including a preview of the incoming event.
        """
        lines: List[Tuple[str, int]] = []
        depth = 1
        lines.append(('raise RuntimeError(', depth))
        depth += 1
        lines.append(
            ('f"Unrecognized event format. No matching handler found for the incoming event:'
             ' {str(event)[:500]}"', depth))
        depth -= 1

        lines.append((')', depth))
        return AWSHandlerGenResponse(self.join_with_depth(lines))
