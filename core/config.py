from urllib.parse import urljoin
from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore"
    )

    authorization_key: str = ""
    controller_api_url: str = ""

    @computed_field # type: ignore[prop-decorator]
    @property
    def authorization_header(self) -> str:
        return f'Bearer {self.authorization_key}'

    @computed_field # type: ignore[prop-decorator]
    @property
    def retrieve_task_url(self) -> str:
        return urljoin(self.controller_api_url, "matrix/task/retrieve-task")

    @computed_field # type: ignore[prop-decorator]
    @property
    def report_result_url(self) -> str:
        return urljoin(self.controller_api_url, "matrix/task/results/")

app_settings = AppSettings()
