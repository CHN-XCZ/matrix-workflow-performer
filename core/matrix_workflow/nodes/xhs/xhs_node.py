from loguru import logger

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from enums.xhs_enums import OperateEnums
from plat.xhs.task_runner import start_script_by_type


class XhsNode(BaseNode):
    _node_type = NodeType.XHS

    def _run(self) -> NodeRunResult:
        try:
            # TODO 获取上级节点的输出结果
            # previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))
            # if not previous_node_outputs:
            #     raise Exception("[XhsNode] run failed: Previous node outputs not found!")
            task_json = self.init_task_json()
            if not task_json:
                raise Exception("[XhsNode] run failed: Task json not found!")
            if self.operate == OperateEnums.COLLECT.value:
                result = start_script_by_type(self.device_id, self.operate, task_json, soft_type=4)
                if len(result) > 0:
                    collect_result = {}
                    collect_result["gather_result"] = result
                    self.result.status = True
                    self.result.outputs = collect_result
                else:
                    self.result.status = False
            else:
                status = start_script_by_type(self.device_id, self.operate, task_json, soft_type=4)
                self.result.status = status
            return self.result
        except Exception as e:
            logger.error("[XhsNode] run error: {}", e)
            self.result.error = str(e)
            return self.result

    def init_task_json(self):
        task_json = {}
        try:
            node_data = self.node_data
            self.result.inputs = {}
            if node_data:
                if self.operate == OperateEnums.POST.value:
                    task_json['content'] = self.variable_pool.get(("run_outputs", node_data["content"][0],node_data["content"][1]))
                    self.result.inputs[node_data["content"][1]]= task_json['content']
                    task_json['title'] = self.variable_pool.get(("run_outputs", node_data["title"][0],node_data["title"][1]))
                    self.result.inputs[node_data["title"][1]]= task_json['title']
                    task_json['img_url'] = self.variable_pool.get(("run_outputs", node_data["img_url"][0],node_data["img_url"][1]))
                    self.result.inputs[node_data["img_url"][1]]= task_json['img_url']
                elif self.operate == OperateEnums.REPLY.value:
                    task_json['xhs_url'] = self.variable_pool.get(("run_outputs", node_data["post_id"][0],node_data["post_id"][1]))
                    self.result.inputs[node_data["post_id"][1]]= task_json['xhs_url']
                    task_json['content'] = self.variable_pool.get(("run_outputs", node_data["content"][0],node_data["content"][1]))
                    self.result.inputs[node_data["content"][1]]= task_json['content']
                elif self.operate == OperateEnums.LIKE.value:
                    task_json['xhs_url'] = self.variable_pool.get(("run_outputs", node_data["post_id"][0],node_data["post_id"][1]))
                    self.result.inputs[node_data["post_id"][1]]= task_json['xhs_url']
                elif self.operate == OperateEnums.FOLLOW.value:
                    task_json['user_id'] = self.variable_pool.get(("run_outputs", node_data["user_id"][0],node_data["user_id"][1]))
                    self.result.inputs[node_data["user_id"][1]]= task_json['user_id']
                elif self.operate == OperateEnums.COLLECT.value:
                    task_json["collect"] = "collect"
                else:
                    logger.error("[XhsNode] init_task_json error: operate not found")
            return task_json
        except Exception as e:
            logger.error("[XhsNode] init_task_json error: {}", e)
            return None