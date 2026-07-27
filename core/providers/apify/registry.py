import os
import yaml
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("jobhunterai.apify_registry")

class ApifyActorRegistry:
    """Loads and manages Apify actor configurations from YAML."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default path relative to project root
            root = Path(__file__).resolve().parent.parent.parent.parent
            config_path = str(root / "config" / "apify_actors.yaml")

        self.config_path = config_path
        self._actors: Dict[str, dict] = {}
        self._health_cache: Dict[str, bool] = {}
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            logger.error(f"Apify config not found at {self.config_path}. Using empty registry.")
            return

        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                scrapers = config.get("scrapers", [])
                local = config.get("local_scrapers", [])

                for s in scrapers + local:
                    self._actors[s["id"]] = s
                    self._health_cache[s["id"]] = True # Assume healthy initially

                logger.info(f"Loaded {len(self._actors)} actors from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to parse Apify config: {e}")

    def get_actor(self, actor_id: str) -> Optional[dict]:
        return self._actors.get(actor_id)

    def get_enabled_actors(self) -> List[dict]:
        enabled = [a for a in self._actors.values() if a.get("enabled", True)]
        return sorted(enabled, key=lambda x: x.get("priority", 999))

    def get_actors_by_capability(self, capability: str) -> List[dict]:
        matches = [a for a in self._actors.values() if capability in a.get("capabilities", [])]
        return sorted(matches, key=lambda x: x.get("priority", 999))

    def mark_actor_healthy(self, actor_id: str):
        self._health_cache[actor_id] = True

    def mark_actor_unhealthy(self, actor_id: str, reason: str = ""):
        logger.warning(f"Actor {actor_id} marked UNHEALTHY. Reason: {reason}")
        self._health_cache[actor_id] = False

    def is_actor_healthy(self, actor_id: str) -> bool:
        return self._health_cache.get(actor_id, True)

# Singleton instance
registry = ApifyActorRegistry()
