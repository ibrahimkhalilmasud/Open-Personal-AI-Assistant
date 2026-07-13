# QUICK START

## Purpose
Get a working local installation in under 10 minutes.

## Audience
Beginners.

## Prerequisites
Python 3.12+, Git.

## Step-by-step
```bash
git clone https://github.com/ibrahimkhalilmasud/Open-Personal-AI-Assistant.git
cd Open-Personal-AI-Assistant
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
Set `VAULT_PATH` in `.env`, add one text file to that folder, then run:
```bash
python main.py --scan
python main.py --index
python main.py --search "your keyword"
python main.py --ask "What do my notes say?"
```

## Examples
```bash
python main.py --memory
python main.py --workflow-list
```

## Troubleshooting
If `--ask` cannot reach cloud/local model, fallback grounded answer still runs from retrieved context.

## Related documents
- [INSTALL.md](INSTALL.md)
- [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)
- [USER_GUIDE.md](USER_GUIDE.md)
