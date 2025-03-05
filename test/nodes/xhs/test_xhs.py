from core.matrix_workflow.graph.graph import Graph
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


def test_xhs():
    config = {
        "edges": [{
            "source": "0",
            "target": "1"
        }
        ],
        "nodes": [{
            "id": "0",
            "type":"start",
            "data":"1"
        }, {
            "id": "1",
            "type":"xhs",
            "data":{
                "operate_cmd":"2",
                "task_json":{
                    "title":"test",
                    "content":"test",
                    "img_url":"https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpeg",
                    "twitter_url":"http://xhslink.com/a/74yBV87HSjC5"
                }
            }
        }],
    }

    graph = Graph.init(config)
    variablePool = VariablePool()

    graphEngine = GraphEngine(graph, variablePool)
    graphEngine.run_graph()