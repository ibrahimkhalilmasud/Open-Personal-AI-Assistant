from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ExtractedEntity:
    name: str
    entity_type: str
    confidence: float


class RuleBasedEntityExtractor:
    _ENTITY_TYPES = {
        "person",
        "organization",
        "country",
        "city",
        "address",
        "airline",
        "hotel",
        "university",
        "research_topic",
        "product",
        "project",
        "date",
        "money",
        "document_title",
        "file_name",
    }

    _COUNTRIES = {
        "belgium",
        "netherlands",
        "germany",
        "france",
        "spain",
        "italy",
        "uk",
        "united kingdom",
        "usa",
        "united states",
        "canada",
        "india",
        "bangladesh",
    }
    _CITIES = {
        "brussels",
        "amsterdam",
        "berlin",
        "paris",
        "london",
        "rome",
        "madrid",
        "new york",
        "toronto",
        "dhaka",
    }

    def extract(self, text: str, source_path: str = "") -> list[ExtractedEntity]:
        candidates: list[ExtractedEntity] = []
        normalized = text or ""

        for value in self._find_people(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type="person", confidence=0.72))

        for value in self._find_organizations(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type="organization", confidence=0.76))

        for value in self._find_locations(normalized):
            candidates.append(value)

        for value in self._find_addresses(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type="address", confidence=0.7))

        for value in self._find_dates(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type="date", confidence=0.8))

        for value in self._find_money(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type="money", confidence=0.85))

        for value, kind in self._find_domain_entities(normalized):
            candidates.append(ExtractedEntity(name=value, entity_type=kind, confidence=0.67))

        if source_path:
            source = Path(source_path)
            candidates.append(ExtractedEntity(name=source.name, entity_type="file_name", confidence=1.0))
            candidates.append(ExtractedEntity(name=source.stem, entity_type="document_title", confidence=0.88))
            parent = source.parent.name.strip()
            if parent:
                candidates.append(ExtractedEntity(name=parent, entity_type="project", confidence=0.6))

        deduped: dict[tuple[str, str], ExtractedEntity] = {}
        for entity in candidates:
            key = (entity.entity_type, entity.name.strip().lower())
            if not entity.name.strip() or entity.entity_type not in self._ENTITY_TYPES:
                continue
            current = deduped.get(key)
            if current is None or entity.confidence > current.confidence:
                deduped[key] = entity
        return sorted(deduped.values(), key=lambda item: (item.entity_type, item.name.lower()))

    def _find_people(self, text: str) -> set[str]:
        names = set(re.findall(r"\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", text))
        names.update(re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", text))
        return {name.strip() for name in names if len(name.split()) <= 4}

    def _find_organizations(self, text: str) -> set[str]:
        pattern = r"\b[A-Z][A-Za-z0-9&\-]*(?:\s+[A-Z][A-Za-z0-9&\-]*)*\s(?:Inc|Ltd|LLC|Company|Corporation|Corp|University|Institute|Airlines|Hotel|Group)\b"
        return {name.strip() for name in re.findall(pattern, text)}

    def _find_locations(self, text: str) -> list[ExtractedEntity]:
        entities: list[ExtractedEntity] = []
        lowered = text.lower()
        for country in self._COUNTRIES:
            if country in lowered:
                entities.append(ExtractedEntity(name=country.title(), entity_type="country", confidence=0.65))
        for city in self._CITIES:
            if city in lowered:
                entities.append(ExtractedEntity(name=city.title(), entity_type="city", confidence=0.65))
        return entities

    def _find_addresses(self, text: str) -> set[str]:
        return {
            value.strip()
            for value in re.findall(r"\b\d{1,5}\s+[A-Z][A-Za-z0-9\-\s]{2,40}\s(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd)\b", text)
        }

    def _find_dates(self, text: str) -> set[str]:
        values = set(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text))
        values.update(re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", text))
        values.update(re.findall(r"\b\d{4}\b", text))
        return values

    def _find_money(self, text: str) -> set[str]:
        values = set(re.findall(r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?", text))
        values.update(re.findall(r"\b\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|BDT)\b", text, flags=re.IGNORECASE))
        return values

    def _find_domain_entities(self, text: str) -> list[tuple[str, str]]:
        matched: list[tuple[str, str]] = []
        patterns = {
            "airline": r"\b[A-Z][A-Za-z]+\s+Airlines?\b",
            "hotel": r"\b(?:Hotel\s+[A-Z][A-Za-z]+|[A-Z][A-Za-z]+\s+Hotel)\b",
            "university": r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+University\b",
            "research_topic": r"\b(?:research|topic)\s*:\s*([A-Za-z0-9\-\s]+)",
            "product": r"\b(?:product|tool|platform)\s*:\s*([A-Za-z0-9\-\s]+)",
            "project": r"\b(?:project|initiative)\s*:\s*([A-Za-z0-9\-\s]+)",
        }
        for kind, pattern in patterns.items():
            for entry in re.findall(pattern, text):
                value = entry if isinstance(entry, str) else " ".join(entry)
                cleaned = value.strip().strip(".,:;")
                if cleaned:
                    matched.append((cleaned, kind))
        return matched


__all__ = ["ExtractedEntity", "RuleBasedEntityExtractor"]
