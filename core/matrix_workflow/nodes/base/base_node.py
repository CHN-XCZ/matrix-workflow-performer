from abc import abstractmethod
from typing import Any, Mapping
from loguru import logger
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.node_type_convert_mapping import node_type_convert_mapping
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


class BaseNode:
    _node_type: NodeType

    def __init__(self, variable_pool: VariablePool, previous_node_id: str, node_data: Mapping[str, Any], device_id: str,
                 operate: int):
        self.variable_pool = variable_pool
        self.previous_node_id = previous_node_id
        self.node_data = node_data
        self.device_id = device_id
        self.operate = operate
        self.result = None

    @abstractmethod
    def _run(self) -> NodeRunResult:
        raise NotImplementedError

    def run(self) -> NodeRunResult | None:
        try:
            node_run_result = NodeRunResult(self.node_data["id"], self.node_data["node_type"],
                                            self.node_data["node_title"], False, None, None, None)

            self.result = node_run_result
            node_type = self.node_data["node_type"]
            if self.node_data["node_type"] in node_type_convert_mapping.keys():
                node_type = node_type_convert_mapping[self.node_data["node_type"]]
            if NodeType(node_type) != NodeType.START:
                node_run_result = self.variable_pool.get(("node_result", self.previous_node_id))
                if isinstance(node_run_result, NodeRunResult):
                    if not node_run_result.status:
                        return None
                    else:
                        return self._run()
            else:
                return self._run()
        except Exception as e:
            self.result.error = str(e)
            logger.error(f"{self.__class__.__name__} run error: {e}")
            return self.result
