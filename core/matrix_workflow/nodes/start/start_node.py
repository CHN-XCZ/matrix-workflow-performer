from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.base.base_node import BaseNode

class StartNode(BaseNode):
    _node_type = NodeType.START

    def _run(self) -> str:
        a = self.variable_pool.get(('input_vars', "a"))

        # return self._node_type
        return a or self._node_type
