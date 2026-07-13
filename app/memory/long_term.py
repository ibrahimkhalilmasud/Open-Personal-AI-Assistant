from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime

from app.database.sqlite_db import fetch_indexable_text_rows
from app.entity_extraction import RuleBasedEntityExtractor
from app.entity_resolution import EntityResolver
from app.knowledge_graph.entities import EntityStore
from app.knowledge_graph.relationships import RelationshipStore
from app.knowledge_graph.timeline import TimelineEngine
from app.memory.preferences import PreferenceMemory
from app.memory.projects import ProjectMemory
from app.summarization import SummaryGenerator


class LongTermMemoryEngine:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.extractor = RuleBasedEntityExtractor()
        self.resolver = EntityResolver()
        self.entities = EntityStore(database_path)
        self.relationships = RelationshipStore(database_path)
        self.timeline = TimelineEngine(database_path)
        self.preferences = PreferenceMemory(database_path)
        self.projects = ProjectMemory(database_path)
        self.summaries = SummaryGenerator(database_path)

    def refresh_from_index(self) -> dict[str, int]:
        rows = fetch_indexable_text_rows(self.database_path)
        processed = 0
        entities_created = 0
        relationships_created = 0
        facts_created = 0

        for row in rows:
            path = str(row.get("path", ""))
            signature = str(row.get("index_signature", "") or row.get("sha256", ""))
            if not path or not signature:
                continue
            if not self._needs_processing(path, signature):
                continue

            text = str(row.get("extracted_text", "") or "")
            modified = str(row.get("modified_date", "") or datetime.now(UTC).isoformat())
            extracted = self.extractor.extract(text, source_path=path)
            resolved = self.resolver.resolve(extracted)

            entity_ids: dict[str, int] = {}
            people: list[str] = []
            for entity in resolved:
                entity_id = self.entities.upsert(
                    canonical_name=entity.canonical_name,
                    entity_type=entity.entity_type,
                    aliases=entity.aliases,
                    confidence=entity.confidence,
                    source_document=path,
                )
                key = f"{entity.entity_type}:{entity.canonical_name}"
                entity_ids[key] = entity_id
                entities_created += 1
                if entity.entity_type == "person":
                    people.append(entity.canonical_name)

            relationships_created += self._create_relationships(resolved, entity_ids, path, text)
            facts_created += self._store_document_facts(text, resolved, path)
            self._store_project_memory(path, people)
            self.timeline.add_event(
                event_date=modified,
                event_type="document_indexed",
                project_name=self.projects.detect_name(path),
                summary=f"Indexed {path}",
                source_document=path,
                confidence=0.9,
            )
            self._update_processing_state(path, signature)
            processed += 1

        self._refresh_project_summaries()
        self._refresh_person_summaries()
        return {
            "processed_files": processed,
            "entities": entities_created,
            "relationships": relationships_created,
            "facts": facts_created,
        }

    def _needs_processing(self, file_path: str, signature: str) -> bool:
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT signature FROM memory_processing_state WHERE file_path = ?",
                (file_path,),
            ).fetchone()
        if row is None:
            return True
        return str(row[0]) != signature

    def _update_processing_state(self, file_path: str, signature: str) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                INSERT INTO memory_processing_state (file_path, signature, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    signature=excluded.signature,
                    updated_at=excluded.updated_at
                """,
                (file_path, signature, datetime.now(UTC).isoformat()),
            )
            conn.commit()

    def _create_relationships(
        self,
        resolved_entities: list[object],
        entity_ids: dict[str, int],
        source_document: str,
        text: str,
    ) -> int:
        count = 0
        for entity in resolved_entities:
            if not hasattr(entity, "entity_type"):
                continue
            source_key = f"{getattr(entity, 'entity_type')}:{getattr(entity, 'canonical_name')}"
            source_id = entity_ids.get(source_key)
            if source_id is None:
                continue

            for target in resolved_entities:
                if entity is target:
                    continue
                target_key = f"{getattr(target, 'entity_type')}:{getattr(target, 'canonical_name')}"
                target_id = entity_ids.get(target_key)
                if target_id is None:
                    continue

                rel_type, confidence = self._relationship_type(
                    source=str(getattr(entity, "canonical_name")),
                    source_type=str(getattr(entity, "entity_type")),
                    target=str(getattr(target, "canonical_name")),
                    target_type=str(getattr(target, "entity_type")),
                    text=text,
                )
                self.relationships.upsert(source_id, target_id, rel_type, confidence, source_document)
                count += 1
        return count

    def _relationship_type(
        self,
        source: str,
        source_type: str,
        target: str,
        target_type: str,
        text: str,
    ) -> tuple[str, float]:
        lowered = text.lower()
        if source_type == "person" and target_type == "organization" and (" works at " in lowered or " works for " in lowered):
            return "works_for", 0.82
        if source_type == "project" and target_type in {"file_name", "document_title"}:
            return "references", 0.74
        if target_type in {"city", "country"} and "travel" in lowered:
            return "travels_to", 0.7
        if target_type in {"organization", "project"} and "belongs" in lowered:
            return "belongs_to", 0.7
        if target_type in {"city", "country", "address"}:
            return "located_in", 0.65
        return "related_to", 0.55

    def _store_document_facts(self, text: str, entities: list[object], source_document: str) -> int:
        facts: list[tuple[str, str, float]] = []

        for match in re.findall(r"\b([A-Z][A-Za-z\s]{1,40})\s+works\s+at\s+([A-Z][A-Za-z0-9\s&\-]{1,50})", text):
            person, org = match
            facts.append((f"{person.strip()} works at {org.strip()}.", person.strip(), 0.82))

        for match in re.findall(r"\b([A-Z][A-Za-z\s]{1,40})\s+expires\s+(\d{4})", text):
            item, year = match
            facts.append((f"{item.strip()} expires {year}.", item.strip(), 0.78))

        for entity in entities:
            if getattr(entity, "entity_type", "") == "project":
                facts.append((f"Project identified: {getattr(entity, 'canonical_name')}.", str(getattr(entity, "canonical_name")), 0.6))

        unique = {(fact, entity_name): confidence for fact, entity_name, confidence in facts}
        now = datetime.now(UTC).isoformat()

        with sqlite3.connect(self.database_path) as conn:
            for (fact, entity_name), confidence in unique.items():
                conn.execute(
                    """
                    INSERT INTO knowledge_memory (fact, entity_name, confidence, source_document, memory_version, timestamp)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (fact, entity_name, max(0.0, min(1.0, confidence)), source_document, now),
                )
            conn.commit()
        return len(unique)

    def _store_project_memory(self, source_path: str, people: list[str]) -> None:
        project = self.projects.detect_name(source_path)
        self.projects.upsert(
            name=project,
            related_files=[source_path],
            related_people=people,
            related_conversations=[],
            summary=f"Project {project} currently tracks {len(people)} people and 1+ files.",
            confidence=0.7,
            source_document=source_path,
        )

    def _refresh_project_summaries(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT name, source_document, confidence FROM projects ORDER BY updated_at DESC"
            ).fetchall()

        for row in rows:
            name = str(row[0])
            source_rows = [
                {
                    "source_document": str(row[1] or ""),
                    "confidence": float(row[2] or 0.0),
                }
            ]
            summary = self.summaries.get_or_refresh("project", name, source_rows)
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("UPDATE projects SET summary = ? WHERE name = ?", (summary, name))
                conn.commit()

    def _refresh_person_summaries(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT canonical_name, source_document, confidence FROM entities WHERE entity_type = 'person'"
            ).fetchall()

        for row in rows:
            name = str(row[0])
            source_rows = [
                {
                    "source_document": str(row[1] or ""),
                    "confidence": float(row[2] or 0.0),
                }
            ]
            self.summaries.get_or_refresh("person", name, source_rows)


__all__ = ["LongTermMemoryEngine"]
