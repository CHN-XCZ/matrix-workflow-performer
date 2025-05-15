from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType


class CodeNode(BaseNode):
    _node_type = NodeType.CODE


    def _run(self) -> NodeRunResult:
        return self.result
