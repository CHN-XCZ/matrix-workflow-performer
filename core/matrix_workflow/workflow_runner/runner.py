from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import requests

from core.matrix_workflow.nodes.node_run_result import DeviceRunResult
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.graph.graph import Graph
from plat.device.adb_device import get_adb_path, get_connected_devices
from loguru import logger

executor = ThreadPoolExecutor(max_workers=200)  # 设备线程池


class MatrixWorkflowRunner:
    def __init__(self, graph_config: dict[str, any]):
        self.graph_config = graph_config

    def run(self):
        graph = Graph.init(self.graph_config) # 初始化图
        variablePool = VariablePool() # 初始化变量池
        future_list = [] # 线程池
        adb_path = get_adb_path() # 获取adb路径
        devices = get_connected_devices(adb_path) # 获取已连接的设备列表
        if not devices: # 如果未找到已连接的设备，则抛出异常
            raise Exception("No connected devices found.")

            # with executor as e:
        for device_id in devices: # 遍历设备列表
            if device_id not in self.graph_config["devices_list"]: # 如果设备未在配置文件中，则跳过
                continue
            graphEngine = GraphEngine(graph, variablePool, device_id) # 初始化设备引擎
            future_list.append(executor.submit(graphEngine.run_graph)) # 提交任务到线程池
            # self.result_mapping = graphEngine.result_mapping
        wait(future_list, return_when=ALL_COMPLETED) # 等待所有任务完成

        # 所有任务完成后输出结果
        flow_run_results = {} #  结果映射
        for future in future_list: # 遍历任务列表
            flow_run_result = DeviceRunResult(status=True, nodes_result=[], error=None) # 初始化设备运行结果
            device_id, result = future.result() # 获取任务结果
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
    post_task_url = "http://192.168.5.125:8000/api/matrix/task/b5a38e84-050c-4ec2-9b5d-8c4db4b9aa9e/generate"
    inputs = {
        "input_variables": {
            "like_post_id": "https://vt.tiktok.com/ZSrQnjG8b/",
            "follow_user_id": "https://www.tiktok.com/@toki.akari?_t=ZS-8vZkEkrINPe&_r=1",
            "title": "111",
            "post_content": "111",
            "post_video_url": "https://redleaf-app.oss-cn-beijing.aliyuncs.com/idolphone/Videos.mp4",
            "comment_post_id": "https://vt.tiktok.com/ZSrQnjG8b/",
            "comment_content": "love you"
        },
        "devices_list": ["bd08f05b"]
    }
    authorization_key = get_config("Authorization_KEY")
    headers = {'Authorization': authorization_key}
    response = requests.post(post_task_url, headers=headers, json=inputs)
    if response.status_code == 201:
        logger.info('post task, request success')
