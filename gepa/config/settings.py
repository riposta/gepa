from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_model: str = "openai/gpt-4o-mini"
    llm_api_base: str = ""
    llm_api_key: str = ""

    graphiti_neo4j_uri: str = "bolt://localhost:7687"
    graphiti_neo4j_user: str = "neo4j"
    graphiti_neo4j_password: str = "password"

    gepa_trigger_threshold: int = 50
    programs_dir: str = "gepa/dspy_modules/programs"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    mlflow_tracking_uri: str = "mlruns"


settings = Settings()
