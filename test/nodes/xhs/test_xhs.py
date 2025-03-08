from core.matrix_workflow.workflow_runner.runner import MatrixWorkflowRunner


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
                    "title":"hhhkl",
                    "content":"hhhkl",
                    "img_url":"https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpeg",
                    "xhs_url":"67c81f10000000002903e864"
                }
            }
        }],
    }

    matrixWorkflowRunner = MatrixWorkflowRunner(config)
    matrixWorkflowRunner.run()