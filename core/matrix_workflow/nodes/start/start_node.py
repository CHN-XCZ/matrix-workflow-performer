from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.base.base_node import BaseNode

class StartNode(BaseNode):
    _node_type = NodeType.START

    def _run(self) -> NodeRunResult:
        self.result.status = True
        return self.result
