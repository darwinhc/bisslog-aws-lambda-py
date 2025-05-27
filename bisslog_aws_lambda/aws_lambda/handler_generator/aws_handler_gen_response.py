"""
Module defining the response structure for AWS Lambda handler code generation.

This module provides a dataclass that encapsulates the components produced during
AWS Lambda handler code generation, including the function body, optional setup code,
and required import statements.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set


@dataclass
class AWSHandlerGenResponse:
    """
    Response structure for generated AWS Lambda handler components.

    This dataclass represents the output of a code generator that produces AWS Lambda
    handler functions. It contains the function body as a string, any optional setup/build
    logic, and the necessary import statements grouped by module.

    Attributes
    ----------
    body : Optional[str]
        The body of the Lambda handler function as a Python code string.
    build : Optional[str]
        Optional setup or preconstruction code to include before the function body.
    importing : Dict[str, List[str]]
        A mapping of module names to lists of symbols to import from them.

        This structure assumes simple `from module import symbol` semantics.

        Examples
        --------
        {
            "typing": ["List", "Optional"],
            "os": ["path", "environ"]
        }

    extra : Dict[str, Any]
        Optional extra data provided by the generator.
    """
    body: Optional[str] = None
    build: Optional[str] = None
    importing: Dict[str, Set[str]] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


    def add_imports(self, new_imports: Dict[str, Set[str]]):
        for module, symbols in new_imports.items():
            if module not in self.importing:
                self.importing[module] = set()
            self.importing[module].update(symbols)

    @staticmethod
    def _generate_imports_string(imports: Dict[str, Set[str]]):
        return "\n".join(f"from {source} import {', '.join(var)}" if var else f"import {source}"
                  for source, var in imports.items())

    def generate_handler_code(self) -> str:
        imports_chunk = self._generate_imports_string(self.importing)

        sep = "\n" * 3
        return (f"{imports_chunk}{sep}{self.build}{sep}"
                f"def lambda_handler(event, context):\n{self.body}\n")

    def __add__(self, other: "AWSHandlerGenResponse") -> "AWSHandlerGenResponse":
        """
        Combine two AWSHandlerGenResponse objects by merging their fields.

        Returns
        -------
        AWSHandlerGenResponse
            A new instance with merged content.
        """
        if not isinstance(other, AWSHandlerGenResponse):
            return NotImplemented

        merged_body = "\n".join(filter(None, [self.body, other.body])) or None
        merged_build = "\n".join(filter(None, [self.build, other.build])) or None

        # Merge importing (sets ensure no duplicates)
        merged_importing: Dict[str, Set[str]] = {}
        for module in set(self.importing) | set(other.importing):
            symbols_self = self.importing.get(module, set())
            symbols_other = other.importing.get(module, set())
            merged_importing[module] = symbols_self.union(symbols_other)

        return AWSHandlerGenResponse(
            body=merged_body,
            build=merged_build,
            importing=merged_importing,
            extra={}  # No
        )


    def __iadd__(self, other: "AWSHandlerGenResponse") -> "AWSHandlerGenResponse":
        """In-place addition of another AWSHandlerGenResponse instance.

        Modifies the current instance by merging the fields from `other`.

        Returns
        -------
        AWSHandlerGenResponse
            The modified instance (self)."""
        if other is None:
            return self
        if not isinstance(other, AWSHandlerGenResponse):
            return NotImplemented

        self.body = "\n".join(filter(None, [self.body, other.body])) or None
        self.build = "\n".join(filter(None, [self.build, other.build])) or None

        for module, symbols in other.importing.items():
            if module not in self.importing:
                self.importing[module] = set()
            self.importing[module].update(symbols)

        self.extra = {}
        return self
