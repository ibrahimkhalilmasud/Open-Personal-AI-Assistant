import argparse
import unittest
from unittest.mock import MagicMock, patch

import main as main_module


class MainCLITests(unittest.TestCase):
    def test_parse_args_supports_phase3_flags(self) -> None:
        with patch("sys.argv", ["main.py", "--index"]):
            args = main_module.parse_args()
        self.assertTrue(args.index)

        with patch("sys.argv", ["main.py", "--search", "insurance renewal"]):
            args = main_module.parse_args()
        self.assertEqual(args.search, "insurance renewal")

        with patch("sys.argv", ["main.py", "--auto-index"]):
            args = main_module.parse_args()
        self.assertTrue(args.auto_index)

        with patch("sys.argv", ["main.py", "--memory"]):
            args = main_module.parse_args()
        self.assertTrue(args.memory)

    @patch("main.create_system")
    @patch("main.VaultEngine")
    def test_main_index_path(self, vault_engine_cls: MagicMock, create_system: MagicMock) -> None:
        args = argparse.Namespace(
            scan=False,
            watch=False,
            index=True,
            auto_index=False,
            search=None,
            folder=None,
            file_type=None,
            after=None,
            before=None,
            top=10,
            memory=False,
            memory_search=None,
            timeline=None,
            project=None,
            person=None,
        )
        with patch("main.parse_args", return_value=args), patch("builtins.print"):
            fake_engine = MagicMock()
            fake_engine.full_scan.return_value = {"total": 1, "new": 1, "changed": 0, "deleted": 0}
            fake_engine.vector_indexer.index_all.return_value = argparse.Namespace(
                indexed=1, updated=0, skipped=0, failed=0, duration_seconds=0.01
            )
            vault_engine_cls.return_value = fake_engine
            create_system.return_value = MagicMock(settings=MagicMock(settings_validation_report="status=ok"))
            main_module.main()
            fake_engine.full_scan.assert_called_once()
            fake_engine.vector_indexer.index_all.assert_called_once()

    @patch("main.RAGEngine")
    @patch("main.create_system")
    def test_main_ask_path(self, create_system: MagicMock, rag_engine_cls: MagicMock) -> None:
        args = argparse.Namespace(
            scan=False,
            watch=False,
            index=False,
            auto_index=False,
            search=None,
            folder=None,
            file_type=None,
            after=None,
            before=None,
            top=10,
            ask="Which documents mention Brussels?",
            model="qwen3",
            stream=False,
        )
        fake_rag = MagicMock()
        fake_rag.ask.return_value = {
            "answer": "Found mention in [C1].",
            "confidence": 0.9,
            "confidence_label": "High",
            "provider": "ollama",
            "model": "qwen3",
            "citations": ["TravelInvoice2025.pdf"],
            "timings": {"retrieval_seconds": 0.1, "context_seconds": 0.1, "model_seconds": 0.2, "total_seconds": 0.4},
        }
        rag_engine_cls.return_value = fake_rag

        with patch("main.parse_args", return_value=args), patch("builtins.print"):
            create_system.return_value = MagicMock(
                settings=MagicMock(settings_validation_report="status=ok"),
                router=MagicMock(),
            )
            main_module.main()
            fake_rag.ask.assert_called_once()


if __name__ == "__main__":
    unittest.main()
