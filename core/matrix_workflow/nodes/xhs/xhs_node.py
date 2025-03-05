import uiautomator2

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_type import NodeType
from xhs.device.adb_device import get_adb_path, get_connected_devices
from xhs.task_runner import start_script_by_type


class XhsNode(BaseNode):
    _node_type = NodeType.XHS

    def _run(self) -> str:
        previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))
        if not previous_node_outputs:
            raise Exception("Minus Node run failed: Previous node outputs not found!")
        adb_path = get_adb_path()
        devices = get_connected_devices(adb_path)
        if not devices:
            raise Exception("No connected devices found.")
        for device_id in devices:

            start_script_by_type(device_id, self.node_data["operate_cmd"], self.node_data["task_json"])
        # TODO: 实现XHS的具体逻辑
        print("Running XHS")
        return "XHS output"