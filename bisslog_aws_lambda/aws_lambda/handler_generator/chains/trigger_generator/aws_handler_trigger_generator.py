"""
Base class for AWS Lambda trigger-based handler generators.

This module defines a common interface and helper methods to generate Python mappers and
handler code based on AWS trigger metadata, such as HTTP, WebSocket, SQS, SNS, or EventBridge.
"""

from abc import ABC, abstractmethod
from json import dumps
from typing import List, Optional, Dict, Tuple, Set

from bisslog_schema.schema import TriggerInfo

from ...aws_handler_gen_response import AWSHandlerGenResponse
from ...aws_handler_generator import AWSHandlerGenerator


class AWSHandlerTriggerGenerator(AWSHandlerGenerator, ABC):
    """
    Abstract base class for AWS Lambda handler generators driven by trigger metadata.

    This class provides utility methods for generating mapper definitions and names,
    which are used to extract request components from incoming AWS events.

    Inheriting classes must implement the `__call__` method to produce a
    trigger-specific `AWSHandlerGenResponse`.

    Inherits
    --------
    AWSHandlerGenerator
        Base generator interface for AWS Lambda handler code.
    """


    @property
    @abstractmethod
    def main_conditional(self) -> str:
        """Property main conditional of a class"""
        raise NotImplementedError()  # pragma: no cover

    @property
    def name_standard_mapper(self) -> str:
        """Property variable name of standard mapper"""
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def generate_mapper_with_requires(
            cls, mapper_name: str,
            mapper_base: Dict[str, str]) -> Tuple[Optional[str], Optional[Set[str]]]:
        """
        Generates a mapper definition string along with a set of required event keys.

        Parameters
        ----------
        mapper_name : str
            The name to assign to the generated Mapper.
        mapper_base : Dict[str, str]
            A dictionary defining how to map event input fields to logical keys.

        Returns
        -------
        Tuple[Optional[str], Optional[Set[str]]]
            A tuple with:
            - The mapper initialization line as a string
            - A set of top-level keys from the event needed by the mapper
        """
        line = cls.generate_mapper(mapper_name, mapper_base)
        if line is None:
            return None, set()
        require = set()
        for source_path in mapper_base.keys():
            require.add(source_path.split(".")[0])
        return line, require

    @classmethod
    def generate_mapper(cls, mapper_name: str, mapper_base: Dict[str, str]) -> Optional[str]:
        """
        Builds the Mapper constructor line based on the provided mapping definition.

        Parameters
        ----------
        mapper_name : str
            The name of the mapper instance in code.
        mapper_base : Dict[str, str]
            A dictionary of mappings from event paths to target keys.

        Returns
        -------
        Optional[str]
            A formatted string to initialize the Mapper, or None if the mapping is empty.
        """
        if mapper_base:
            return f'{mapper_name} = Mapper("{mapper_name}", {dumps(mapper_base)})'
        return None

    @staticmethod
    def generate_mapper_name(trigger_type: str, keyname: Optional[str], i: int) -> str:
        """
        Constructs a unique name for a Mapper instance based on trigger context.

        Parameters
        ----------
        trigger_type : str
            Type of the trigger (e.g., "http", "sqs").
        keyname : Optional[str]
            Optional keyname identifier from the trigger.
        i : int
            Index of the trigger in its list.

        Returns
        -------
        str
            A unique mapper name string.
        """
        return f"mapper_{trigger_type}_{i}" + ("" if keyname is None else f"_{keyname}")

    @staticmethod
    def trigger_valid(trigger) -> bool:
        """
        Abstract method to check if a trigger is valid for this generator.

        Parameters
        ----------
        trigger : TriggerInfo
            The trigger metadata instance to validate.

        Returns
        -------
        bool
            True if the trigger is valid for this generator, False otherwise.

        Raises
        ------
        NotImplementedError
            If not implemented in a subclass.
        """
        raise NotImplementedError()  # pragma: no cover


    def start(
            self, triggers: List[TriggerInfo], trigger_valid, mapper_name: str, mapper_base: dict,
            depth = 1
    ) -> Optional[Tuple[List[TriggerInfo], List[Tuple[str, int]], List[str], int, bool]]:
        """
        Sub-call method to be implemented by subclasses for generating handler code.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            List of trigger metadata instances attached to the use case.
        trigger_valid: Function
            Func to validate if a trigger is applicable for this generator.
        mapper_name : str
            Name of the mapper to be used in the handler code.
        mapper_base : dict
            Base mapping definition for the mapper to be used in the handler.

        depth : int, optional
            The initial indentation depth for the generated code, by default 1.

        Returns
        -------
        Optional[Tuple[List[TriggerInfo], List[Tuple[str, int]], List[str], int, bool]]
            A tuple containing:
            - Valid triggers after filtering
            - Lines of code to be generated
            - Pre-build lines for mappers
            - Updated depth for indentation
            - Boolean indicating if only a single trigger is present
        """
        triggers_ok = list(filter(trigger_valid, triggers))
        if not triggers_ok:
            return None

        is_single = len(triggers_ok) == 1
        lines: List[Tuple[str, int]] = [(self.main_conditional, depth)]
        depth += 1

        pre_build_lines = [
            self.generate_mapper(mapper_name, mapper_base)]

        return triggers_ok, lines, pre_build_lines, depth, is_single

    @staticmethod
    def comm(line: str):
        """Comment line"""
        return "# " + line

    @abstractmethod
    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        """
        Abstract method to generate handler code based on a list of triggers.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            List of trigger metadata instances attached to the use case.
        uc_var_name : str
            Variable name that represents the use case object in the handler.

        Returns
        -------
        Optional[AWSHandlerGenResponse]
            A response containing handler code and supporting imports/builds,
            or None if the generator does not handle the provided triggers.

        Raises
        ------
        NotImplementedError
            If not implemented in a subclass.
        """

        raise NotImplementedError()  # pragma: no cover
