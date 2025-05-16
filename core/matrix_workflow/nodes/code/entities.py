from collections.abc import Sequence
from typing import Literal, Optional
from pydantic import BaseModel

from core.helper.code_executor.executor import CodeLanguage

class VariableSelector(BaseModel):
    """
    Variable Selector
    """

    variable: str
    variable_selector: Sequence[str]

class CodeNodeData(BaseModel):
    """
    Code Node Data.
    """

    class Output(BaseModel):
        type: Literal["string", "number", "object", "array[string]", "array[number]", "array[object]"]
        children: Optional[dict[str, "CodeNodeData.Output"]] = None

    class Dependency(BaseModel):
        name: str
        version: str

    variables: list[VariableSelector]
    code_language: Literal[CodeLanguage.PYTHON3, CodeLanguage.JAVASCRIPT]
    code: str
    outputs: dict[str, Output]
    dependencies: Optional[list[Dependency]] = None
