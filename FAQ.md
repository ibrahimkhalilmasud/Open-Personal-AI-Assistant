# FAQ

## Purpose
Answer common questions quickly.

## Audience
All users.

## Prerequisites
Installed project.

## Step-by-step (Q&A)
1. **Does it support local-only use?** Yes, local-first with Ollama/local fallback modes.
2. **Which AI providers are implemented?** Ollama, Gemini, Groq, OpenAI.
3. **Which CLI commands are available?** Run `python main.py --help`.
4. **Is there a `--setup` or `--backup` command?** No, these flags are not implemented in `main.py`.
5. **Where are logs?** `logs/` directory.
6. **How do I test quickly?** Use [QUICK_START.md](QUICK_START.md).

## Examples
```bash
python main.py --help
python main.py --workflow-list
```

## Troubleshooting
If behavior differs from docs, check your branch and rerun `python main.py --help`.

## Related documents
- [README.md](README.md)
- [INSTALL.md](INSTALL.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
