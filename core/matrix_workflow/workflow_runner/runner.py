from typing import Any, Mapping
import uuid

from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool
from core.matrix_workflow.graph.graph_engine import GraphEngine
from core.matrix_workflow.graph.graph import Graph
from app.schemas.matrix_workflow import MatrixWorkflowGraph
from app.api.dep import DBSessoinDep
from app.crud.matrix_workflow import get_matrix_workflow

class MatrixWorkflowRunner:
    def __init__(self, *, inputs_vars: Mapping[str, Any], workflow_id: uuid.UUID, db_session: DBSessoinDep):
        self.input_vars = inputs_vars
        self.db_session = db_session
        self.workflow_id = workflow_id

    async def run(self):
        workflow = await get_matrix_workflow(self.db_session, self.workflow_id)

        if not workflow:
            raise Exception("Workflow not found")



        variable_pool = VariablePool(input_variables=self.input_vars)

        graph = MatrixWorkflowGraph.parse_raw(workflow.graph)
        graph_cls_instance = Graph.init(graph.dict())
        graph_engine = GraphEngine(graph=graph_cls_instance, variable_pool=variable_pool)
        running_result = graph_engine.run_graph()

        return {
            "variables_pool": variable_pool.variable_dict,
            "running_result": running_result
        }
