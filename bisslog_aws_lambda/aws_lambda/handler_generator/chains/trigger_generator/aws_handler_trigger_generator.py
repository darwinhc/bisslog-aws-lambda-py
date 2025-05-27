from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple, Set

from json import dumps

from bisslog_schema.schema import TriggerInfo

from ...aws_handler_generator import AWSHandlerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class AWSHandlerTriggerGenerator(AWSHandlerGenerator, ABC):

    @classmethod
    def generate_mapper_with_requires(
            cls, mapper_name : str,
            mapper_base: Dict[str, str]) -> Tuple[Optional[str], Optional[Set[str]]]:
        line = cls.generate_mapper(mapper_name, mapper_base)
        if line is None:
            return None, set()
        require = set()
        for source_path in mapper_base.keys():
            require.add(source_path.split(".")[0])
        return line, require

    @classmethod
    def generate_mapper(cls, mapper_name: str, mapper_base: Dict[str, str]) -> Optional[str]:
        if mapper_base:
            return f"""{mapper_name} = Mapper("{mapper_name}", {dumps(mapper_base)})"""
        return None

    @staticmethod
    def generate_mapper_name(trigger_type: str, keyname: Optional[str], i: int):
        return f"mapper_{trigger_type}_{i}" + ("" if keyname is None else f"_{keyname}")

    @abstractmethod
    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        raise NotImplementedError()
