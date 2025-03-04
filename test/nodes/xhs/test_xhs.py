from core.matrix_workflow.graph.graph import Graph
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


def test_xhs():
    config = {
        "edges": [{
            "source": "0",
            "target": "1"
        }, {
            "source": "1",
            "target": "2"
        }],
        "nodes": [{
            "id": "0",
            "type":"start",
            "data":"1"
        }, {
            "id": "1",
            "type":"xhs",
            "data":"1"
        }, {
            "id": "2",
            "type":"xhs",
            "data":"1"
        }],
    }

    graph = Graph.init(config)
    variablePool = VariablePool()

    graphEngine = GraphEngine(graph, variablePool)
    graphEngine.run_graph()