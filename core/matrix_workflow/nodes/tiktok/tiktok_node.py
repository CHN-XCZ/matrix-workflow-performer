from loguru import logger

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from enums.tiktok_enums import OperateEnums
from plat.task_runner import start_script_by_type


class TikTokNode(BaseNode):
    _node_type = NodeType.TIKTOK

    def _run(self) -> NodeRunResult:
        try:
            # TODO 获取上级节点的输出结果
            # previous_node_outputs = self.variable_pool.get(("run_outputs", self.previous_node_id))
            # if not previous_node_outputs:
            #     raise Exception("[XhsNode] run failed: Previous node outputs not found!")
            task_json = self.init_task_json()
            if not task_json:
                raise Exception("[TikTokNode] run failed: Task json not found!")
            result = start_script_by_type(self.device_id, self.operate, task_json, soft_type=6)
            if self.operate == OperateEnums.COLLECT.value:
                if len(result) > 0:
                    collect_result = {}
                    collect_result["gather_result"] = result
                    self.result.status = True
                    self.result.outputs = collect_result
                else:
                    self.result.status = False
            elif self.operate == OperateEnums.POST.value:
                post_result = {}
                post_result["post_url"] = result
                self.result.status = True
                self.result.outputs = post_result
            else:
                self.result.status = result
            return self.result
        except Exception as e:
            logger.error("[TikTokNode] run error: {}", e)
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
                    if node_data["title"]:
                        task_json['title'] = self.variable_pool.get(("run_outputs", node_data["title"][0],node_data["title"][1]))
                        self.result.inputs[node_data["title"][1]]= task_json['title']
                    else:
                        task_json["title"] = None
                    # task_json['title'] = self.variable_pool.get(("run_outputs", node_data["title"][0],node_data["title"][1]))
                    # self.result.inputs[node_data["title"][1]]= task_json['title']
                    task_json['img_url'] = self.variable_pool.get(("run_outputs", node_data["media_url"][0],node_data["media_url"][1]))
                    self.result.inputs[node_data["media_url"][1]]= task_json['img_url']
                elif self.operate == OperateEnums.REPLY.value:
                    task_json['post_url'] = self.variable_pool.get(("run_outputs", node_data["post_id"][0],node_data["post_id"][1]))
                    self.result.inputs[node_data["post_id"][1]]= task_json['post_url']
                    task_json['content'] = self.variable_pool.get(("run_outputs", node_data["content"][0],node_data["content"][1]))
                    self.result.inputs[node_data["content"][1]]= task_json['content']
                elif self.operate == OperateEnums.LIKE.value:
                    task_json['post_url'] = self.variable_pool.get(("run_outputs", node_data["post_id"][0],node_data["post_id"][1]))
                    self.result.inputs[node_data["post_id"][1]]= task_json['post_url']
                elif self.operate == OperateEnums.FOLLOW.value:
                    task_json['user_id'] = self.variable_pool.get(("run_outputs", node_data["user_id"][0],node_data["user_id"][1]))
                    self.result.inputs[node_data["user_id"][1]]= task_json['user_id']
                elif self.operate == OperateEnums.COLLECT.value:
                    task_json["collect"] = "collect"
                else:
                    logger.error("[TikTokNode] init_task_json error: operate not found")
            return task_json
        except Exception as e:
            logger.error("[TikTokNode] init_task_json error: {}", e)
            return None