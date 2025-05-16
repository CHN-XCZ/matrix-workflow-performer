from enum import Enum
from collections.abc import Mapping
from typing import Any, Optional

from pydantic import BaseModel
from httpx import post, Timeout
from yarl import URL

from core.config import app_settings
from core.helper.code_executor.template_transformer import TemplateTransformer
from core.helper.code_executor.javascript.javascript_transformer import NodeJsTemplateTransformer
from core.helper.code_executor.python3.python_transformer import Python3TemplateTransformer


class CodeLanguage(str, Enum):
    PYTHON3 = "python3"
    JAVASCRIPT = "javascript"

class CodeExecutionResponse(BaseModel):
    class Data(BaseModel):
        stdout: Optional[str] = None
        error: Optional[str] = None

    code: int
    message: str
    data: Data

class CodeExecutor:

    code_template_transformers: dict[CodeLanguage, type[TemplateTransformer]] = {
        CodeLanguage.PYTHON3: Python3TemplateTransformer,
        CodeLanguage.JAVASCRIPT: NodeJsTemplateTransformer,
    }

    code_language_to_running_language = {
        CodeLanguage.JAVASCRIPT: "nodejs",
        CodeLanguage.PYTHON3: CodeLanguage.PYTHON3,
    }

    supported_dependencies_languages: set[CodeLanguage] = {CodeLanguage.PYTHON3}

    @classmethod
    def execute_code(cls, language: CodeLanguage, preload: str, code: str) -> str:
        """
        Execute code
        :param language: code language
        :param code: code
        :return:
        """
        url = URL(str(app_settings.code_execution_endpoint)) / "v1" / "sandbox" / "run"

        headers = {"X-Api-Key": app_settings.code_execution_api_key}

        data = {
            "language": cls.code_language_to_running_language.get(language),
            "code": code,
            "preload": preload,
            "enable_network": True,
        }

        try:
            response = post(
                str(url),
                json=data,
                headers=headers,
                timeout=Timeout(
                    connect=10.0,
                    read=60.0,
                    write=60.0,
                    pool=None,
                ),
            )
            if response.status_code == 503:
                raise Exception("Code execution service is unavailable")
            elif response.status_code != 200:
                raise Exception(
                    f"Failed to execute code, got status code {response.status_code},"
                    f" please check if the sandbox service is running"
                )
        except Exception as e:
            raise e

        try:
            response = response.json()
        except:
            raise Exception("Failed to parse response")

        if (code := response.get("code")) != 0:
            raise Exception(f"Got error code: {code}. Got error msg: {response.get('message')}")

        response = CodeExecutionResponse(**response)

        if response.data.error:
            raise Exception(response.data.error)

        return response.data.stdout or ""

    @classmethod
    def execute_workflow_code_template(cls, language: CodeLanguage, code: str, inputs: Mapping[str, Any]) -> dict:
        """
        Execute code
        :param language: code language
        :param code: code
        :param inputs: inputs
        :return:
        """
        template_transformer = cls.code_template_transformers.get(language)
        if not template_transformer:
            raise Exception(f"Unsupported language {language}")

        runner, preload = template_transformer.transform_caller(code, inputs)

        try:
            response = cls.execute_code(language, preload, runner)
        except Exception as e:
            raise e

        return template_transformer.transform_response(response)
