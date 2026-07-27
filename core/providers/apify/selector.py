import logging
from typing import List, Optional
from core.providers.apify.registry import registry as default_registry

logger = logging.getLogger("jobhunterai.apify_selector")

class ApifyActorSelector:
    """Chooses the best Apify actor for a given job search query."""

    def __init__(self, registry_instance=None):
        self.registry = registry_instance or default_registry

    def _infer_capabilities_from_query(self, query: str) -> List[str]:
        query_lower = query.lower()
        capabilities = []

        keywords = {
            "linkedin": "linkedin",
            "indeed": "indeed",
            "google": "google",
            "remote": "remote",
            "intern": "internship"
        }

        for kw, cap in keywords.items():
            if kw in query_lower:
                capabilities.append(cap)

        return capabilities

    def select_actor(self, query: str, location: str = "") -> Optional[dict]:
        """Choose a single best actor."""
        actors = self.select_actors_parallel(query, count=1)
        return actors[0] if actors else None

    def select_actors_parallel(self, query: str, count: int = 3) -> List[dict]:
        """Returns top N actors suitable for the query, sorted by weighted priority."""
        enabled = self.registry.get_enabled_actors()
        inferred = self._infer_capabilities_from_query(query)

        scored_actors = []
        for actor in enabled:
            score = actor.get("priority", 999)

            # 1. Match inferred capabilities
            for cap in inferred:
                if cap in actor.get("capabilities", []):
                    score -= 5 # Boost priority

            # 2. Penalty for unhealthy
            if not self.registry.is_actor_healthy(actor["id"]):
                score += 50

            scored_actors.append((score, actor))

        # Sort by score ascending (lower is better)
        scored_actors.sort(key=lambda x: x[0])

        results = [a[1] for a in scored_actors[:count]]
        logger.info(f"Selected {len(results)} actors for query '{query}': {[a['id'] for a in results]}")
        return results

# Singleton instance
selector = ApifyActorSelector()
