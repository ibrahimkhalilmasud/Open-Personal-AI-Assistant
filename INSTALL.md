# INSTALLATION GUIDE

## Purpose
Install the assistant on Windows, Linux, macOS, WSL, and Docker.

## Audience
First-time users and administrators.

## Prerequisites
- Git
- Python 3.12+
- Internet access for dependency/model downloads
- Optional AI keys: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`

## Step-by-step
### 1) Install Python and Git
- Windows: install Python and Git from official installers.
- macOS: `brew install python git`
- Linux: `sudo apt install -y python3 python3-venv git`

### 2) Clone repository
```bash
git clone https://github.com/ibrahimkhalilmasud/Open-Personal-AI-Assistant.git
cd Open-Personal-AI-Assistant
```

### 3) Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 4) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Create `.env`
```bash
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
```
Set at minimum:
```env
VAULT_PATH=/absolute/path/to/your/personal-vault
```

### 6) Choose AI provider
- Local default: `OLLAMA_URL=http://localhost:11434`, `DEFAULT_MODEL=qwen3`
- Cloud optional: set one or more keys in `.env`

### 7) Create Personal Vault
```bash
mkdir -p "$VAULT_PATH"
echo "Insurance policy renewal is in March." > "$VAULT_PATH/insurance.txt"
```

### 8) Run setup verification flow
```bash
python main.py --scan
python main.py --index
python main.py --search "insurance"
python main.py --ask "Summarize my insurance"
python main.py --health
python main.py --status
python main.py --metrics
```

### 9) Platform installers
- Linux: `bash installers/install_linux.sh`
- macOS: `bash installers/install_macos.sh`
- Windows: `installers\install_windows.bat`

### 10) Docker
```bash
cp .env.example .env
# edit VAULT_PATH to a valid path inside container mount strategy
docker compose up --build
```

### 11) WSL
Use Linux instructions inside WSL; keep vault under Linux filesystem for best performance.

## Examples
```bash
python main.py --sdk-test
python main.py --api --host 127.0.0.1 --port 8000
```

## Troubleshooting
- Missing module error: run `pip install -r requirements.txt` in active venv.
- `VAULT_PATH` warning: set it in `.env`.
- Chroma unavailable: local vector fallback is used automatically.

## Related documents
- [QUICK_START.md](QUICK_START.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [SECURITY.md](SECURITY.md)
