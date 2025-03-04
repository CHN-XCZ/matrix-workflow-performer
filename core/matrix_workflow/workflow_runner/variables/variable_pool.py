from typing import Mapping, Union, Any
from collections import defaultdict
from collections.abc import Sequence

from pydantic import BaseModel,Field

VariableValue = Union[str, int, float, dict, list]

class VariablePool(BaseModel):
    variable_dict: dict[str, dict[int, Any]] = Field(
        description="variable dictionary",
        default=defaultdict(dict)
    )
    input_variables: Mapping[str, Any] = Field(
            description="inputs",
    )

    def __init__(self, *, input_variables: Mapping[str, Any] | None = None, **kwargs):

        input_variables = input_variables or {}

        super().__init__(
            input_variables=input_variables,
            **kwargs
        )

        for key, value in self.input_variables.items():
            self.add(('input_vars', key), value)


    def get(self, selector: Sequence[str], /) -> Any | None:
        if len(selector) < 2:
            return None

        hash_key = hash(tuple(selector[1:]))

        return self.variable_dict[selector[0]].get(hash_key)


    def add(self, selector: Sequence[str], value: Any, /) -> None:
        if len(selector) < 2:
            raise ValueError('Variable dict selector invalid')

        hash_key = hash(tuple(selector[1:]))

        self.variable_dict[selector[0]][hash_key] = value


    def remove(self, selector: Sequence[str], /):

        if not selector:
            return
        if len(selector) == 1:
            self.variable_dict[selector[0]] = {}
            return
        hash_key = hash(tuple[selector[1:]])
        self.variable_dict[selector[0]].pop(hash_key, None)
