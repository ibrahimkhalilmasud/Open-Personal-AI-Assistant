from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResolvedEntity:
    canonical_name: str
    entity_type: str
    aliases: list[str]
    confidence: float


class EntityResolver:
    def resolve(self, entities: list[dict[str, str | float]] | list[object]) -> list[ResolvedEntity]:
        grouped: dict[tuple[str, str], ResolvedEntity] = {}

        for item in entities:
            if hasattr(item, "name"):
                name = str(getattr(item, "name", "")).strip()
                entity_type = str(getattr(item, "entity_type", "related_to")).strip().lower()
                confidence = float(getattr(item, "confidence", 0.5) or 0.5)
            else:
                row = item if isinstance(item, dict) else {}
                name = str(row.get("name", "")).strip()
                entity_type = str(row.get("entity_type", "related_to")).strip().lower()
                confidence = float(row.get("confidence", 0.5) or 0.5)

            if not name:
                continue
            canonical = self._canonicalize(name)
            key = (entity_type, canonical)
            current = grouped.get(key)
            if current is None:
                grouped[key] = ResolvedEntity(
                    canonical_name=canonical,
                    entity_type=entity_type,
                    aliases=[name],
                    confidence=max(0.0, min(1.0, confidence)),
                )
                continue

            if name not in current.aliases:
                current.aliases.append(name)
            current.confidence = max(current.confidence, max(0.0, min(1.0, confidence)))

        return sorted(grouped.values(), key=lambda item: (item.entity_type, item.canonical_name))

    def _canonicalize(self, value: str) -> str:
        lowered = value.lower().strip()
        prefixes = ("mr ", "mr. ", "mrs ", "mrs. ", "ms ", "ms. ", "dr ", "dr. ")
        for prefix in prefixes:
            if lowered.startswith(prefix):
                lowered = lowered[len(prefix) :]
                break
        tokens = [token for token in lowered.replace("_", " ").replace("-", " ").split() if token]
        if not tokens:
            return value.strip()
        return " ".join(tokens).title()


__all__ = ["EntityResolver", "ResolvedEntity"]
