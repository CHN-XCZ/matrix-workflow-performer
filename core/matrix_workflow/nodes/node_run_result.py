class NodeRunResult:
    node_id: str
    node_type: str
    node_title: str
    status: bool
    inputs: dict[str, any] | None
    outputs: dict[str, any] | None
    error: str | None

    def __init__(self, node_id: str, node_type: str, node_title: str, status: bool, inputs: dict[str, any] | None, outputs: dict[str, any] | None, error: str | None):
        self.node_id = node_id
        self.node_type = node_type
        self.node_title = node_title
        self.status = status
        self.inputs = inputs
        self.outputs = outputs
        self.error = error

    def to_dict(self):
        # 将对象属性转换为字典
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "node_title": self.node_title,
            "status": self.status,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "error": self.error
        }

class DeviceRunResult:
    status: bool
    nodes_result: list[NodeRunResult]
    error: str | None

    def __init__(self, status: bool, nodes_result: list[NodeRunResult], error: str | None):
        self.status = status
        self.nodes_result = nodes_result
        self.error = error

    def to_dict(self):
        # 递归转换所有嵌套对象
        return {
            "status": self.status,
            "nodes_result": [node.to_dict() for node in self.nodes_result],
            "error": self.error
        }