"""Boundary for an optional NVIDIA Auto Ontology deployment.

The local semantic adapter is deliberately the default. A deployed Auto Ontology
instance may be connected later without exposing its credentials to the React UI.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AutoOntologyIntegration:
    base_url: str | None

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def status(self) -> dict[str, str | bool | None]:
        return {
            "enabled": self.enabled,
            "base_url": self.base_url if self.enabled else None,
            "mode": "external semantic service" if self.enabled else "local semantic adapter",
        }


integration = AutoOntologyIntegration(os.getenv("AUTO_ONTOLOGY_URL") or None)

