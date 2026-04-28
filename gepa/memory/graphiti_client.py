from datetime import datetime, timezone

import openai
from graphiti_core import Graphiti
from graphiti_core.embedder.azure_openai import AzureOpenAIEmbedderClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client import LLMConfig
from graphiti_core.llm_client.azure_openai_client import AzureOpenAILLMClient
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient

from gepa.config.settings import settings


def _build_graphiti_clients(
    api_key: str,
    model: str,
    base_url: str | None,
    api_version: str | None,
) -> tuple:
    """Returns (llm_client, embedder) matched to the model provider."""
    provider = model.split("/")[0].lower() if "/" in model else "openai"
    bare_model = model.split("/", 1)[1] if "/" in model else model

    if provider == "azure":
        azure_openai = openai.AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url or "",
            api_version=api_version or "2024-02-01",
        )
        llm_config = LLMConfig(api_key=api_key, model=bare_model, base_url=base_url)
        return (
            AzureOpenAILLMClient(azure_client=azure_openai, config=llm_config),
            AzureOpenAIEmbedderClient(azure_client=azure_openai),
        )

    if provider == "openai":
        llm_config = LLMConfig(api_key=api_key, model=bare_model, base_url=base_url)
        embedder_config = OpenAIEmbedderConfig(api_key=api_key, base_url=base_url)
        return (
            OpenAIClient(config=llm_config),
            OpenAIEmbedder(config=embedder_config),
        )

    # OpenAI-compatible: Ollama, Groq, Together, local servers, etc.
    llm_config = LLMConfig(api_key=api_key, model=bare_model, base_url=base_url)
    embedder_config = OpenAIEmbedderConfig(api_key=api_key, base_url=base_url)
    return (
        OpenAIGenericClient(config=llm_config),
        OpenAIEmbedder(config=embedder_config),
    )


class GraphitiClient:
    def __init__(self) -> None:
        api_key = settings.llm_api_key.get_secret_value()
        base_url = settings.llm_api_base or None
        api_version = settings.llm_api_version or None

        llm_client, embedder = _build_graphiti_clients(
            api_key=api_key,
            model=settings.llm_model,
            base_url=base_url,
            api_version=api_version,
        )
        self.graphiti = Graphiti(
            settings.graphiti_neo4j_uri,
            settings.graphiti_neo4j_user,
            settings.graphiti_neo4j_password.get_secret_value(),
            llm_client=llm_client,
            embedder=embedder,
        )

    async def get_context(self, client: str, project_description: str, project_type: str = "new") -> str:
        results = await self.graphiti.search(
            f"project history {project_type} client {client}: {project_description}"
        )
        if not results:
            return "No client history in knowledge base."
        return "\n".join(r.fact for r in results[:5])

    async def get_risk_patterns(self, project_description: str) -> str:
        results = await self.graphiti.search(
            f"risk patterns estimation: {project_description}"
        )
        if not results:
            return "No learned risk patterns."
        return "\n".join(r.fact for r in results[:3])

    async def add_episode(self, session_id: str, content: str) -> None:
        await self.graphiti.add_episode(
            name=session_id,
            episode_body=content,
            source_description="estimation_agent",
            reference_time=datetime.now(tz=timezone.utc),
        )

    async def close(self) -> None:
        await self.graphiti.close()
