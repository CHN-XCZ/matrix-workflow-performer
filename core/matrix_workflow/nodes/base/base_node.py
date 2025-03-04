from abc import abstractmethod
from typing import Any, Mapping
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


class BaseNode:
    _node_type: NodeType

    def __init__(self, variable_pool: VariablePool, previous_node_id: str, node_data: Mapping[str, Any]):
        self.variable_pool = variable_pool
        self.previous_node_id = previous_node_id
        self.node_data = node_data

    @abstractmethod
    def _run(self) -> str:
        raise NotImplementedError

    def run(self) -> str:
        return self._run()
