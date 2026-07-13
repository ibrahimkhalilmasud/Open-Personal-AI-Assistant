# Open Personal AI Assistant (Version 1.0)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Tests](https://img.shields.io/badge/tests-unittest-brightgreen)

Local-first personal AI assistant with vault scanning, hybrid search, RAG answers, persistent memory, knowledge graph, task workflows, tools, plugins, REST API, and Python SDK.

## Purpose
Provide a complete, beginner-friendly entry point to install, run, and operate the project.

## Audience
New users, contributors, and maintainers.

## Prerequisites
- Python 3.12+
- Git
- Optional: Ollama or cloud API keys (OpenAI/Groq/Gemini)

## Step-by-step
1. Clone and enter repository.
2. Create virtual environment.
3. Install dependencies.
4. Copy `.env.example` to `.env` and set `VAULT_PATH`.
5. Run first scan/index/search.

```bash
git clone https://github.com/ibrahimkhalilmasud/Open-Personal-AI-Assistant.git
cd Open-Personal-AI-Assistant
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set VAULT_PATH
python main.py --scan
python main.py --index
python main.py --search "insurance"
```

## Examples
```bash
python main.py --help
python main.py --ask "Summarize my insurance"
python main.py --memory
python main.py --api
```

## Verified CLI Commands
`--scan --watch --index --auto-index --search --folder --type --after --before --top --ask --model --stream --agents --agent-list --workflow-list --plan --execute --memory --memory-search --timeline --project --person --api --health --status --metrics --sdk-test --host --port`

## API Summary
- Public: `/`, `/health`, `/status`, `/metrics`, `/docs`, `/openapi.json`
- Protected (`X-API-Key`): `/api/v1/search`, `/memory`, `/vault`, `/rag`, `/tasks`, `/workflows`, `/tools`, `/plugins`, `/system`

## Troubleshooting
- If model downloads fail, use local/cached embeddings or retry with network access.
- If `VAULT_PATH` is empty, scan/index commands will fail.
- If `--watch` fails, ensure `watchdog` is installed.

## Related documents
- [INSTALL.md](INSTALL.md)
- [QUICK_START.md](QUICK_START.md)
- [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md)
- [WORKFLOW_EXAMPLES.md](WORKFLOW_EXAMPLES.md)
- [API_REFERENCE.md](API_REFERENCE.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [CHANGELOG.md](CHANGELOG.md)
