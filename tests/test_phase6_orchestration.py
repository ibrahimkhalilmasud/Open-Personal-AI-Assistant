import tempfile
import unittest
from pathlib import Path

from app.agents.executor import AgentExecutor
from app.agents.history import AgentHistoryStore
from app.agents.registry import AgentRegistry
from app.tasks.executor import TaskExecutionEngine
from app.tasks.models import PENDING, Task, now_iso
from app.tasks.planner import TaskPlanner
from app.tasks.queue import TaskQueue
from app.tasks.history import TaskHistoryStore


class _FakeContext:
    def to_dict(self):
        return {"retrieved_documents": [{"path": "vault/doc1.md", "filename": "doc1.md"}]}


class _FakeContextEngine:
    def build(self, title: str, description: str):
        return _FakeContext()


class Phase6OrchestrationTests(unittest.TestCase):
    def test_agent_registry_discovers_planning_agent(self) -> None:
        registry = AgentRegistry()
        registry.discover()

        agent = registry.get_agent("planning-agent")
        self.assertIsNotNone(agent)
        self.assertIn("planning", agent.capabilities)

    def test_task_planner_builds_dependency_chain(self) -> None:
        registry = AgentRegistry()
        registry.discover()
        planner = TaskPlanner(registry)

        tasks = planner.plan("Prepare my Bali business trip.", requested_by="tester")

        self.assertGreaterEqual(len(tasks), 2)
        self.assertEqual(tasks[0].status, PENDING)
        self.assertFalse(tasks[0].approved)
        self.assertEqual(tasks[1].dependencies, [tasks[0].task_id])

    def test_task_queue_persists_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "queue.db")
            queue = TaskQueue(db_path)
            task = Task(
                task_id="task-1",
                title="Step 1",
                description="Collect data",
                priority=1,
                status=PENDING,
                created_at=now_iso(),
                updated_at=now_iso(),
                requested_by="tester",
                assigned_agent="planning-agent",
                dependencies=[],
                execution_log=[],
                result={},
                confidence=0.0,
                citations=[],
                approved=False,
                retries=0,
                workflow="",
            )
            queue.enqueue(task)

            reloaded = TaskQueue(db_path)
            found = reloaded.get_task("task-1")
            self.assertIsNotNone(found)
            self.assertEqual(found.description, "Collect data")

    def test_execution_runs_sequentially_when_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "tasks.db")
            queue = TaskQueue(db_path)

            registry = AgentRegistry()
            registry.discover()
            history = AgentHistoryStore(db_path)
            task_history = TaskHistoryStore(db_path)
            agent_executor = AgentExecutor(registry, _FakeContextEngine(), history)
            engine = TaskExecutionEngine(queue, agent_executor, task_history)

            first = Task(
                task_id="t1",
                title="Step 1",
                description="Find passport.",
                priority=2,
                status=PENDING,
                created_at=now_iso(),
                updated_at=now_iso(),
                requested_by="tester",
                assigned_agent="planning-agent",
                dependencies=[],
                execution_log=[],
                result={},
                confidence=0.0,
                citations=[],
                approved=False,
                retries=0,
                workflow="travel_preparation_workflow",
            )
            second = Task(
                task_id="t2",
                title="Step 2",
                description="Check passport expiry.",
                priority=1,
                status=PENDING,
                created_at=now_iso(),
                updated_at=now_iso(),
                requested_by="tester",
                assigned_agent="planning-agent",
                dependencies=["t1"],
                execution_log=[],
                result={},
                confidence=0.0,
                citations=[],
                approved=False,
                retries=0,
                workflow="travel_preparation_workflow",
            )
            queue.enqueue_many([first, second])

            results = engine.execute(approve_pending=True)

            self.assertEqual(len(results), 2)
            self.assertTrue(all(item.success for item in results))
            self.assertEqual(queue.get_task("t1").status, "completed")
            self.assertEqual(queue.get_task("t2").status, "completed")


if __name__ == "__main__":
    unittest.main()
