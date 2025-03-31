from typing import Any, Union, cast
from core.matrix_workflow.nodes.node_type import NodeType

class Edge:
    target_node_id: str
    source_node_id: str

    def __init__(self, target_node_id: str, source_node_id: str, edge_id: str):
        self.target_node_id = target_node_id
        self.source_node_id = source_node_id
        self.edge_id = edge_id


class Graph:
    root_node_id: str
    node_id_list: list[str]=[]
    node_id_data_mapping: dict[str, dict]={}
    source_node_edge_mapping: dict[str, list[Edge]]={}
    input_variables: dict[str, Any]={}

    @classmethod
    def init(cls, graph_data: dict[str, Any]) -> "Graph":
        input_list = graph_data.get("input_variables")
        node_list = graph_data.get("graph").get("nodes")
        edge_list = graph_data.get("graph").get("edges")
        if node_list is None or edge_list is None:
            raise Exception('Nodes or Edges not found in Graph')

        input_list = cast(dict[str, Any], input_list)
        node_list = cast(list[dict[str, Any]], node_list)
        edge_list = cast(list[dict[str, Any]], edge_list)

        source_node_edge_mapping={}

        graph = cls()

        graph.input_variables = input_list

        for edge in edge_list:
            source_node_id = edge.get("source")
            target_node_id = edge.get("target")
            edge_id = edge.get("id")

            if not source_node_id or not target_node_id or not edge_id:
                continue

            if source_node_id not in source_node_edge_mapping:
                source_node_edge_mapping[source_node_id] = []

            new_edge = Edge(target_node_id=target_node_id, source_node_id=source_node_id, edge_id=edge_id)

            source_node_edge_mapping[source_node_id].append(new_edge)


        graph.source_node_edge_mapping = source_node_edge_mapping

        root_node_id: Union[str, None] = None

        for node in node_list:
            if node["data"]["node_type"] == NodeType.START:
                root_node_id = node["id"]

            graph.node_id_list.append(node["id"])
            graph.node_id_data_mapping.update({node["id"]: node})

        if not root_node_id:
            raise Exception('No root node found!')

        graph.root_node_id = root_node_id

        return graph
