from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import requests

from core.matrix_workflow.nodes.node_run_result import DeviceRunResult
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.graph.graph import Graph
from plat.xhs.device.adb_device import get_adb_path, get_connected_devices
from loguru import logger

executor = ThreadPoolExecutor(max_workers=200)  # 设备线程池


class MatrixWorkflowRunner:
    def __init__(self, graph_config: dict[str, any]):
        self.graph_config = graph_config

    def run(self):
        graph = Graph.init(self.graph_config)
        variablePool = VariablePool()
        future_list = []
        adb_path = get_adb_path()
        devices = get_connected_devices(adb_path)
        if not devices:
            raise Exception("No connected devices found.")

            # with executor as e:
        for device_id in devices:
            graphEngine = GraphEngine(graph, variablePool, device_id)
            future_list.append(executor.submit(graphEngine.run_graph))
            # self.result_mapping = graphEngine.result_mapping
        wait(future_list, return_when=ALL_COMPLETED)

        # 所有任务完成后输出结果
        flow_run_results = {}
        for future in future_list:
            flow_run_result = DeviceRunResult(status=True, nodes_result=[], error=None)
            device_id, result = future.result()
            for e in result:
                if not e.status:
                    flow_run_result.status = False
                    flow_run_result.error = e.error
            flow_run_result.nodes_result = result
            flow_run_results[device_id] = flow_run_result
        # post_task()
        return flow_run_results

    # 临时生成任务


def post_task():
    post_task_url = "http://192.168.5.135:8000/api/matrix/task/f57e1cb3-e33e-474e-a5b8-0df03efadb5c/generate"
    inputs = {
        "input_variables": {
            "like_id": "64",
            "follow_id": "57",
            "title": "111",
            "img": "1111",
            "content": "1111"
        }
    }
    response = requests.post(post_task_url, json=inputs)
    if response.status_code == 201:
        logger.info('post task, request success')
