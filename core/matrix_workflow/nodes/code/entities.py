from collections.abc import Sequence
from typing import Literal, Optional
from pydantic import BaseModel

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

    variables: list[VariableSelector]
    code_language: Literal[]
