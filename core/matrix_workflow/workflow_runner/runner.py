from concurrent.futures import ThreadPoolExecutor

from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.graph.graph import Graph
from xhs.device.adb_device import get_adb_path, get_connected_devices

executor = ThreadPoolExecutor(max_workers=200)  # 设备线程池
class MatrixWorkflowRunner:
    def __init__(self, graph_config: dict[str, any], result_mapping: dict[str, any]):
        self.graph_config = graph_config
        self.result_mapping = result_mapping


    def run(self):
        graph = Graph.init(self.graph_config)
        variablePool = VariablePool()
        adb_path = get_adb_path()
        devices = get_connected_devices(adb_path)
        if not devices:
            raise Exception("No connected devices found.")
        for device_id in devices:
            graphEngine = GraphEngine(graph, variablePool, device_id, self.result_mapping)
            executor.submit(graphEngine.run_graph())