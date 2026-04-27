from datetime import datetime, timezone

from graphiti_core import Graphiti

from gepa.config.settings import settings


class GraphitiClient:
    def __init__(self) -> None:
        self.graphiti = Graphiti(
            settings.graphiti_neo4j_uri,
            settings.graphiti_neo4j_user,
            settings.graphiti_neo4j_password.get_secret_value(),
        )

    async def get_context(self, klient: str, opis_projektu: str) -> str:
        results = await self.graphiti.search(
            f"historia projektów klienta {klient}: {opis_projektu}"
        )
        if not results:
            return "Brak historii klienta w bazie wiedzy."
        # EntityEdge has a 'fact' field with the knowledge graph fact text
        return "\n".join(r.fact for r in results[:5])

    async def get_risk_patterns(self, opis_projektu: str) -> str:
        results = await self.graphiti.search(
            f"wzorce ryzyk wycena: {opis_projektu}"
        )
        if not results:
            return "Brak wyuczonych wzorców ryzyk."
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
