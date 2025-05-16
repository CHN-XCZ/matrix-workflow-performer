from collections.abc import Mapping, Sequence
from typing import Any, Optional

from loguru import logger

from core.helper.code_executor.executor import CodeExecutor
from core.matrix_workflow.nodes.base.base_node import BaseNode
from core.matrix_workflow.nodes.node_run_result import NodeRunResult
from core.matrix_workflow.nodes.node_type import NodeType
from core.matrix_workflow.nodes.code.entities import CodeNodeData

CODE_MAX_NUMBER=9223372036854775807
CODE_MIN_NUMBER=-9223372036854775808
CODE_MAX_STRING_LENGTH=80000
TEMPLATE_TRANSFORM_MAX_LENGTH=80000
CODE_MAX_STRING_ARRAY_LENGTH=30
CODE_MAX_OBJECT_ARRAY_LENGTH=30
CODE_MAX_NUMBER_ARRAY_LENGTH=1000
CODE_MAX_PRECISION=20
CODE_MAX_DEPTH=5

class CodeNode(BaseNode):
    _node_type = NodeType.CODE


    def _run(self) -> NodeRunResult:

        try:
            code_node_data = self._init_code_node_data()

            code_language = code_node_data.code_language
            code = code_node_data.code

            variables = {}
            for variable_selector in code_node_data.variables:
                variable_name = variable_selector.variable
                variable = self.variable_pool.get(["run_outputs", *variable_selector.variable_selector])
                variables[variable_name] = variable


            result = CodeExecutor.execute_workflow_code_template(
                language=code_language,
                code=code,
                inputs=variables
            )

            # format result
            result = self._transform_result(result=result, output_schema=code_node_data.outputs)

            # add result to variable pool
            for key in result:
                self.variable_pool.add(("run_outputs", self.node_id, key), result[key])

            self.result.inputs = variables
            self.result.outputs = result
            self.result.status = True

            return self.result

        except Exception as e:
            logger.error("[CodeNode] run error: {}", e)
            self.result.error = str(e)
            return self.result

    def _init_code_node_data(self) -> CodeNodeData:
        return CodeNodeData(**self.node_data)

    def _check_string(self, value: str | None, variable: str) -> str | None:
        """
        Check string
        :param value: value
        :param variable: variable
        :return:
        """
        if value is None:
            return None
        if not isinstance(value, str):
            raise Exception(f"Output variable `{variable}` must be a string")

        if len(value) > CODE_MAX_STRING_LENGTH:
            raise Exception(
                f"The length of output variable `{variable}` must be"
                f" less than {CODE_MAX_STRING_LENGTH} characters"
            )

        return value.replace("\x00", "")

    def _check_number(self, value: int | float | None, variable: str) -> int | float | None:
        """
        Check number
        :param value: value
        :param variable: variable
        :return:
        """
        if value is None:
            return None
        if not isinstance(value, int | float):
            raise Exception(f"Output variable `{variable}` must be a number")

        if value > CODE_MAX_NUMBER or value < CODE_MIN_NUMBER:
            raise Exception(
                f"Output variable `{variable}` is out of range,"
                f" it must be between {CODE_MIN_NUMBER} and {CODE_MAX_NUMBER}."
            )

        if isinstance(value, float):
            # raise error if precision is too high
            if len(str(value).split(".")[1]) > CODE_MAX_PRECISION:
                raise Exception(
                    f"Output variable `{variable}` has too high precision,"
                    f" it must be less than {CODE_MAX_PRECISION} digits."
                )

        return value

    def _transform_result(
        self,
        result: Mapping[str, Any],
        output_schema: Optional[dict[str, CodeNodeData.Output]],
        prefix: str = "",
        depth: int = 1,
    ):
        if depth > CODE_MAX_DEPTH:
            raise Exception(f"Depth limit ${CODE_MAX_DEPTH} reached, object too deep.")

        transformed_result: dict[str, Any] = {}
        if output_schema is None:
            # validate output thought instance type
            for output_name, output_value in result.items():
                if isinstance(output_value, dict):
                    self._transform_result(
                        result=output_value,
                        output_schema=None,
                        prefix=f"{prefix}.{output_name}" if prefix else output_name,
                        depth=depth + 1,
                    )
                elif isinstance(output_value, int | float):
                    self._check_number(
                        value=output_value, variable=f"{prefix}.{output_name}" if prefix else output_name
                    )
                elif isinstance(output_value, str):
                    self._check_string(
                        value=output_value, variable=f"{prefix}.{output_name}" if prefix else output_name
                    )
                elif isinstance(output_value, list):
                    first_element = output_value[0] if len(output_value) > 0 else None
                    if first_element is not None:
                        if isinstance(first_element, int | float) and all(
                            value is None or isinstance(value, int | float) for value in output_value
                        ):
                            for i, value in enumerate(output_value):
                                self._check_number(
                                    value=value,
                                    variable=f"{prefix}.{output_name}[{i}]" if prefix else f"{output_name}[{i}]",
                                )
                        elif isinstance(first_element, str) and all(
                            value is None or isinstance(value, str) for value in output_value
                        ):
                            for i, value in enumerate(output_value):
                                self._check_string(
                                    value=value,
                                    variable=f"{prefix}.{output_name}[{i}]" if prefix else f"{output_name}[{i}]",
                                )
                        elif isinstance(first_element, dict) and all(
                            value is None or isinstance(value, dict) for value in output_value
                        ):
                            for i, value in enumerate(output_value):
                                if value is not None:
                                    self._transform_result(
                                        result=value,
                                        output_schema=None,
                                        prefix=f"{prefix}.{output_name}[{i}]" if prefix else f"{output_name}[{i}]",
                                        depth=depth + 1,
                                    )
                        else:
                            raise Exception(
                                f"Output {prefix}.{output_name} is not a valid array."
                                f" make sure all elements are of the same type."
                            )
                elif output_value is None:
                    pass
                else:
                    raise Exception(f"Output {prefix}.{output_name} is not a valid type.")

            return result

        parameters_validated = {}
        for output_name, output_config in output_schema.items():
            dot = "." if prefix else ""
            if output_name not in result:
                raise Exception(f"Output {prefix}{dot}{output_name} is missing.")

            if output_config.type == "object":
                # check if output is object
                if not isinstance(result.get(output_name), dict):
                    if isinstance(result.get(output_name), type(None)):
                        transformed_result[output_name] = None
                    else:
                        raise Exception(
                            f"Output {prefix}{dot}{output_name} is not an object,"
                            f" got {type(result.get(output_name))} instead."
                        )
                else:
                    transformed_result[output_name] = self._transform_result(
                        result=result[output_name],
                        output_schema=output_config.children,
                        prefix=f"{prefix}.{output_name}",
                        depth=depth + 1,
                    )
            elif output_config.type == "number":
                # check if number available
                transformed_result[output_name] = self._check_number(
                    value=result[output_name], variable=f"{prefix}{dot}{output_name}"
                )
            elif output_config.type == "string":
                # check if string available
                transformed_result[output_name] = self._check_string(
                    value=result[output_name],
                    variable=f"{prefix}{dot}{output_name}",
                )
            elif output_config.type == "array[number]":
                # check if array of number available
                if not isinstance(result[output_name], list):
                    if isinstance(result[output_name], type(None)):
                        transformed_result[output_name] = None
                    else:
                        raise Exception(
                            f"Output {prefix}{dot}{output_name} is not an array,"
                            f" got {type(result.get(output_name))} instead."
                        )
                else:
                    if len(result[output_name]) > CODE_MAX_NUMBER_ARRAY_LENGTH:
                        raise Exception(
                            f"The length of output variable `{prefix}{dot}{output_name}` must be"
                            f" less than {CODE_MAX_NUMBER_ARRAY_LENGTH} elements."
                        )

                    transformed_result[output_name] = [
                        self._check_number(value=value, variable=f"{prefix}{dot}{output_name}[{i}]")
                        for i, value in enumerate(result[output_name])
                    ]
            elif output_config.type == "array[string]":
                # check if array of string available
                if not isinstance(result[output_name], list):
                    if isinstance(result[output_name], type(None)):
                        transformed_result[output_name] = None
                    else:
                        raise Exception(
                            f"Output {prefix}{dot}{output_name} is not an array,"
                            f" got {type(result.get(output_name))} instead."
                        )
                else:
                    if len(result[output_name]) > CODE_MAX_STRING_ARRAY_LENGTH:
                        raise Exception(
                            f"The length of output variable `{prefix}{dot}{output_name}` must be"
                            f" less than {CODE_MAX_STRING_ARRAY_LENGTH} elements."
                        )

                    transformed_result[output_name] = [
                        self._check_string(value=value, variable=f"{prefix}{dot}{output_name}[{i}]")
                        for i, value in enumerate(result[output_name])
                    ]
            elif output_config.type == "array[object]":
                # check if array of object available
                if not isinstance(result[output_name], list):
                    if isinstance(result[output_name], type(None)):
                        transformed_result[output_name] = None
                    else:
                        raise Exception(
                            f"Output {prefix}{dot}{output_name} is not an array,"
                            f" got {type(result.get(output_name))} instead."
                        )
                else:
                    if len(result[output_name]) > CODE_MAX_OBJECT_ARRAY_LENGTH:
                        raise Exception(
                            f"The length of output variable `{prefix}{dot}{output_name}` must be"
                            f" less than {CODE_MAX_OBJECT_ARRAY_LENGTH} elements."
                        )

                    for i, value in enumerate(result[output_name]):
                        if not isinstance(value, dict):
                            if value is None:
                                pass
                            else:
                                raise Exception(
                                    f"Output {prefix}{dot}{output_name}[{i}] is not an object,"
                                    f" got {type(value)} instead at index {i}."
                                )

                    transformed_result[output_name] = [
                        None
                        if value is None
                        else self._transform_result(
                            result=value,
                            output_schema=output_config.children,
                            prefix=f"{prefix}{dot}{output_name}[{i}]",
                            depth=depth + 1,
                        )
                        for i, value in enumerate(result[output_name])
                    ]
            else:
                raise Exception(f"Output type {output_config.type} is not supported.")

            parameters_validated[output_name] = True

        # check if all output parameters are validated
        if len(parameters_validated) != len(result):
            raise Exception("Not all output parameters are validated.")

        return transformed_result

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: CodeNodeData,
    ) -> Mapping[str, Sequence[str]]:
        """
        Extract variable selector to variable mapping
        :param graph_config: graph config
        :param node_id: node id
        :param node_data: node data
        :return:
        """
        return {
            node_id + "." + variable_selector.variable: variable_selector.value_selector
            for variable_selector in node_data.variables
        }
