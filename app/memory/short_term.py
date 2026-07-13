from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class ShortTermTurn:
    question: str
    answer: str
    timestamp: str


class ShortTermMemory:
    def __init__(self, capacity: int = 20) -> None:
        self._turns: deque[ShortTermTurn] = deque(maxlen=max(1, capacity))

    def add(self, question: str, answer: str, timestamp: str) -> None:
        self._turns.append(ShortTermTurn(question=question, answer=answer, timestamp=timestamp))

    def recent(self) -> list[ShortTermTurn]:
        return list(self._turns)


__all__ = ["ShortTermMemory", "ShortTermTurn"]
