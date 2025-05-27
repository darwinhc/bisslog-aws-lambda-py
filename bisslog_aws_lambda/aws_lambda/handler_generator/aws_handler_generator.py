from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

from .aws_handler_gen_response import AWSHandlerGenResponse


class AWSHandlerGenerator(ABC):

    indent = "    "




    @abstractmethod
    def __call__(self, *args, **kwargs) -> AWSHandlerGenResponse:
        raise NotImplementedError

    def join_with_depth(self, lines_with_depth: List[Tuple[str, int]]) -> str:
        return "\n".join(depth * self.indent + line for line, depth in lines_with_depth)