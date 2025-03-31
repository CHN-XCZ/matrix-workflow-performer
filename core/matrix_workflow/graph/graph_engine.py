from core.matrix_workflow.graph.graph import Graph
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.node_type_class_mapping import node_type_class_mapping
from core.matrix_workflow.nodes.node_type_convert_mapping import node_type_convert_mapping, node_operate_convert_mapping
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


class GraphEngine:

    def __init__(self, graph: Graph, variable_pool: VariablePool, device_id: str):
        self.graph = graph
        self.variable_pool = variable_pool
        self.device_id = device_id
        # self.result_mapping = result_mapping

    def run_graph(
            self,
    ):

        # edge_mapping = {
        #     key: [vars(edge) for edge in edge_list]
        #     for key, edge_list in self.graph.source_node_edge_mapping.items()
        # }

        start_node_id = self.graph.root_node_id
        # parallel_start_node_id = None
        next_node_id = start_node_id
        previous_node_id = start_node_id

        result_list = []
        try:
            while True:
                current_node_id = next_node_id

                current_node_config = self.graph.node_id_data_mapping.get(current_node_id)
                if not current_node_config:
                    raise Exception(f"Run Error: node config of {current_node_id} not found!")

                # 操作类型
                operate = -1

                node_type = current_node_config.get("data").get('node_type')
                if node_type in node_type_convert_mapping:
                    convert_type = node_type_convert_mapping[node_type]
                    operate = node_operate_convert_mapping[node_type]
                    current_node_type = NodeType(convert_type)
                else:
                    current_node_type = NodeType(node_type)

                current_node_data = current_node_config.get("data")

                if not current_node_data:
                    raise Exception(f"data of node {current_node_id} not found!")

                current_node_cls = node_type_class_mapping[current_node_type]

                current_node_instance = current_node_cls(variable_pool=self.variable_pool,
                                                         previous_node_id=previous_node_id, node_data=current_node_data,
                                                         device_id=self.device_id, operate=operate)

                current_node_run_result = current_node_instance.run()

                if not current_node_run_result:
                    raise Exception(f"Run Error: node {current_node_id} run failed!")
                # 将输入参数添加到变量池中
                if current_node_type == NodeType.START:
                    current_node_run_result.inputs = self.graph.input_variables
                    for key, value in self.graph.input_variables.items():
                        self.variable_pool.add(("run_outputs", current_node_id, key), value)

                # 将节点运行结果添加到变量池中
                self.variable_pool.add(("node_result", current_node_id), current_node_run_result)

                # 将输出参数添加到变量池中
                if current_node_run_result.outputs is not None and current_node_run_result.status:
                    for key, value in current_node_run_result.outputs.items():
                        self.variable_pool.add(("run_outputs", current_node_id, key), value)

                result_list.append(current_node_run_result)

                if current_node_type == NodeType.END:
                    break

                # get next node
                # TODO: CHECK PARALLEL
                edge_mappings = self.graph.source_node_edge_mapping.get(next_node_id)
                if not edge_mappings:
                    break

                edge = edge_mappings[len(edge_mappings)-1]
                if current_node_type == NodeType.IF_ELSE:
                    for ed in edge_mappings:
                        if current_node_run_result.outputs["result"] and current_node_run_result.outputs["selected_case_id"] in ed.edge_id:
                            edge = ed


                next_node_id = edge.target_node_id
                previous_node_id = current_node_id
            # self.result_mapping = result_list
        except Exception as e:
            from loguru import logger
            logger.error(f"Run Error: {e}")
        finally:
            return self.device_id, result_list
