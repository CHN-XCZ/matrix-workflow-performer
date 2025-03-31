from typing import Literal, Optional

from pydantic import BaseModel, Field

from core.matrix_workflow.utils.condition.entities import Condition

class Case(BaseModel):
        """
        Case entity representing a single logical condition group
        """

        case_id: str
        logical_operator: Literal["and", "or"]
        conditions: list[Condition]
