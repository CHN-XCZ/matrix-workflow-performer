from typing import Literal

from typing_extensions import deprecated

from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.if_else.entities import Case
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.utils.condition.entities import Condition
from core.matrix_workflow.utils.condition.processor import ConditionProcessor
from core.matrix_workflow.workflow_runner.variables.variable_pool import VariablePool


def model_validate_json(json_data):
    cases: list[Case] = []
    for case in json_data:
        cases.append(Case(**case))
    return cases


class IfElseNode(BaseNode):
    _node_type = NodeType.IF_ELSE

    def _run(self) -> NodeRunResult:
        """
        Run node
        :return:
        """
        node_inputs: dict[str, list] = {"conditions": []}

        process_data: dict[str, list] = {"condition_results": []}

        input_conditions = []
        final_result = False
        selected_case_id = None
        condition_processor = ConditionProcessor()
        try:
            # Check if the new cases structure is used

            if self.node_data["cases"]:
                cases = model_validate_json(self.node_data["cases"])
                for case in cases:
                    input_conditions, group_result, final_result = condition_processor.process_conditions(
                        variable_pool=self.variable_pool,
                        conditions=case.conditions,
                        operator=case.logical_operator,
                    )

                    process_data["condition_results"].append(
                        {
                            "group": case.model_dump(),
                            "results": group_result,
                            "final_result": final_result,
                        }
                    )

                    # Break if a case passes (logical short-circuit)
                    if final_result:
                        selected_case_id = case.case_id  # Capture the ID of the passing case
                        break

            else:
                input_conditions, group_result, final_result = _should_not_use_old_function(
                    condition_processor=condition_processor,
                    variable_pool=self.variable_pool,
                    conditions=self.node_data["conditions"] or [],
                    operator=self.node_data["logical_operator"] or "and",
                )

                selected_case_id = "true" if final_result else "false"

                process_data["condition_results"].append(
                    {"group": "default", "results": group_result, "final_result": final_result}
                )

            node_inputs["conditions"] = input_conditions

        except Exception as e:
            self.result.status=False
            self.result.error = str(e)
            return self.result

        outputs = {"result": final_result, "selected_case_id": selected_case_id}
        self.result.status=True
        self.result.inputs = node_inputs
        self.result.outputs = outputs

        return self.result


@deprecated("This function is deprecated. You should use the new cases structure.")
def _should_not_use_old_function(
    *,
    condition_processor: ConditionProcessor,
    variable_pool: VariablePool,
    conditions: list[Condition],
    operator: Literal["and", "or"],
):
    return condition_processor.process_conditions(
        variable_pool=variable_pool,
        conditions=conditions,
        operator=operator,
    )
