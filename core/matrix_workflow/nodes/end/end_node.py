from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.base.base_node import BaseNode

class EndNode(BaseNode):
    _node_type = NodeType.END

    def _run(self) -> str:
        return self._node_type
