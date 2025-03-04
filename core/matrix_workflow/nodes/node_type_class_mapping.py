from core.matrix_workflow.nodes.node_type import NodeType

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.start.start_node import StartNode
from core.matrix_workflow.nodes.end.end_node import EndNode
from core.matrix_workflow.nodes.add.add_node import AddNode
from core.matrix_workflow.nodes.minus.minus_node import MinusNode
from core.matrix_workflow.nodes.xhs.xhs_node import XhsNode

node_type_class_mapping: dict[NodeType, type[BaseNode]] = {
    NodeType.START: StartNode,
    NodeType.END: EndNode,
    NodeType.ADD: AddNode,
    NodeType.MINUS: MinusNode,
    NodeType.XHS: XhsNode
}
