from abc import abstractmethod
from typing import Any, Mapping
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


class BaseNode:
    _node_type: NodeType

    def __init__(self, variable_pool: VariablePool, previous_node_id: str, node_data: Mapping[str, Any], device_id:str, result_mapping: dict[str, any]):
        self.variable_pool = variable_pool
        self.previous_node_id = previous_node_id
        self.node_data = node_data
        self.device_id = device_id
        self.result_mapping = result_mapping

    @abstractmethod
    def _run(self) -> str:
        raise NotImplementedError

    def run(self) -> str:
        return self._run()
