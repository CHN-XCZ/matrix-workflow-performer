from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_type import NodeType


class XhsNode(BaseNode):
    _node_type = NodeType.XHS

    def _run(self) -> str:
        previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))
        if not previous_node_outputs:
            raise Exception("Minus Node run failed: Previous node outputs not found!")
        # TODO: 实现XHS的具体逻辑
        print("Running XHS")
        return "XHS output"