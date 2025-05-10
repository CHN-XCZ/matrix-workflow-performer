from core.matrix_workflow.nodes.facebook.face_node import FaceBookNode
from core.matrix_workflow.nodes.if_else import IfElseNode
from core.matrix_workflow.nodes.node_type import NodeType

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.start.start_node import StartNode
from core.matrix_workflow.nodes.http_request.node import HttpRequestNode
from core.matrix_workflow.nodes.end.end_node import EndNode
from core.matrix_workflow.nodes.xhs.xhs_node import XhsNode
from core.matrix_workflow.nodes.tiktok.tiktok_node import TikTokNode

node_type_class_mapping: dict[NodeType, type[BaseNode]] = {
    NodeType.START: StartNode,
    NodeType.END: EndNode,
    NodeType.IF_ELSE: IfElseNode,
    NodeType.HTTP_REQUEST: HttpRequestNode,
    NodeType.XHS: XhsNode,
    NodeType.FACEBOOK: FaceBookNode,
    NodeType.TIKTOK: TikTokNode
}
