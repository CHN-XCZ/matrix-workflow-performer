from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.base.base_node import BaseNode

class MinusNode(BaseNode):
    _node_type = NodeType.MINUS

    def _run(self) -> str:
        previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))

        if not previous_node_outputs:
            raise Exception("Minus Node run failed: Previous node outputs not found!")

        try:
            previous_node_outputs_number = float(previous_node_outputs)
            return str(previous_node_outputs_number - 10.0)
        except ValueError:
            raise Exception("Minus Node run failed: Previous node outputs is not number!")
        except:
            raise Exception("Minus Node run failed: unknown issue!")
