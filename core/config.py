from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

load_dotenv()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore"
    )

    authorization_key: str = ""
    controller_api_url: str = ""
    code_execution_endpoint: str = ""
    code_execution_api_key: str = ""

    @computed_field # type: ignore[prop-decorator]
    @property
    def authorization_header(self) -> str:
        return f'Bearer {self.authorization_key}'

    @computed_field # type: ignore[prop-decorator]
    @property
    def retrieve_task_url(self) -> str:
        url = URL(self.controller_api_url) / "matrix" / "task" / "retrieve-task"
        return str(url)

    @computed_field # type: ignore[prop-decorator]
    @property
    def report_result_url(self) -> str:
        url = URL(self.controller_api_url) / "matrix" / "task" / "results"
        return str(url)

app_settings = AppSettings()
