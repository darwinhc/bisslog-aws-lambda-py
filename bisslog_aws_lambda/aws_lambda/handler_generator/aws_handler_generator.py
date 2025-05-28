"""
Abstract base class for AWS Lambda handler generators.

This module defines the common interface and utilities shared across
different AWS handler generators (e.g., HTTP, WebSocket, EventBridge).
"""
from abc import ABC, abstractmethod
from typing import List, Tuple

from .aws_handler_gen_response import AWSHandlerGenResponse


class AWSHandlerGenerator(ABC):
    """
    Abstract base class for generating AWS Lambda handler code.

    Subclasses must implement the `__call__` method to return an `AWSHandlerGenResponse`
    object. This base class provides utility methods for code formatting.

    Attributes
    ----------
    indent : str
        The string used to represent one indentation level (default: 4 spaces).
    """

    indent = "    "

    @abstractmethod
    def __call__(self, *args, **kwargs) -> AWSHandlerGenResponse:
        """Aws handler generator method.

        Returns
        -------
        AWSHandlerGenResponse
            The generated Lambda handler response object.
        """
        raise NotImplementedError  # pragma: no cover

    def join_with_depth(self, lines_with_depth: List[Tuple[str, int]]) -> str:
        """
        Joins lines of code using the given indentation depth per line.

        Parameters
        ----------
        lines_with_depth : List[Tuple[str, int]]
            A list of tuples where each tuple contains:
            - The code line as a string
            - The indentation depth as an integer

        Returns
        -------
        str
            The formatted multi-line string with proper indentation.
        """
        return "\n".join(depth * self.indent + line for line, depth in lines_with_depth)
