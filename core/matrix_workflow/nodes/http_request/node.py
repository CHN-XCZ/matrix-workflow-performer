from loguru import logger
import json

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.http_request.entities import HttpRequestNodeData, HttpRequestNodeTimeout
from core.matrix_workflow.nodes.http_request.executor import Executor

HTTP_REQUEST_DEFAULT_TIMEOUT = HttpRequestNodeTimeout(
    connect=300,
    read=600,
    write=600,
)

class HttpRequestNode(BaseNode):
    _node_type = NodeType.HTTP_REQUEST

    @classmethod
    def get_default_config(cls, filters: dict | None = None) -> dict:
        return {
            "type": "http-request",
            "config": {
                "method": "get",
                "authorization": {
                    "type": "no-auth",
                },
                "body": {"type": "none"},
                "timeout": {
                    "max_connect_timeout": 300,
                    "max_read_timeout": 600,
                    "max_write_timeout": 600,
                },
            },
        }

    def _run(self) -> NodeRunResult:
        process_data = {}

        try:
            request_node_data = self._init_request_data()

            http_executor = Executor(
                            node_data=request_node_data,
                            timeout=self._get_request_timeout(request_node_data),
                            variable_pool=self.variable_pool,
                        )
            process_data["request"] = http_executor.to_log()

            response = http_executor.invoke()
            # files = self.extract_files(url=http_executor.url, response=response)

            outputs={
                "status_code": response.status_code,
                # "body": response.text if not files else "",
                "body": response.text,
                "headers": response.headers,
                "process_data": process_data
                #"files": files
            }

            self.variable_pool.add(("run_outputs", self.node_id, "status_code"), response.status_code)
            self.variable_pool.add(("run_outputs", self.node_id, "body"), response.text)
            self.variable_pool.add(("run_outputs", self.node_id, "headers"), response.headers)

            self.result.outputs = outputs
            self.result.status = True

            return self.result

        except Exception as e:
            logger.error("[HttpRequestNode] run error: {}", e)
            self.result.error = str(e)
            return self.result

    def _init_request_data(self) -> HttpRequestNodeData:
        return HttpRequestNodeData(**self.node_data)


    @staticmethod
    def _get_request_timeout(node_data: HttpRequestNodeData) -> HttpRequestNodeTimeout:
        timeout = node_data.timeout
        if timeout is None:
            return HTTP_REQUEST_DEFAULT_TIMEOUT

        timeout.connect = timeout.connect or HTTP_REQUEST_DEFAULT_TIMEOUT.connect
        timeout.read = timeout.read or HTTP_REQUEST_DEFAULT_TIMEOUT.read
        timeout.write = timeout.write or HTTP_REQUEST_DEFAULT_TIMEOUT.write
        return timeout
