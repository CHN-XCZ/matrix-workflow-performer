from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_type import NodeType
from plat.task_runner import start_script_by_type


class FaceBookNode(BaseNode):
    _node_type = NodeType.FACEBOOK

    def _run(self):
        previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))
        if not previous_node_outputs:
            raise Exception("Minus Node run failed: Previous node outputs not found!")

        result = start_script_by_type(self.device_id, self.node_data["operate_cmd"], self.node_data["task_json"], soft_type=5)

        return result