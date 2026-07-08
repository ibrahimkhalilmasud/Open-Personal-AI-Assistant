# INSTALL

## Python

Use Python 3.12+.

## Windows 10/11
Run `installers\\install_windows.bat`.

## Linux (Ubuntu 24.04, Debian, Mint)
Run:
```bash
bash installers/install_linux.sh
```

## macOS
Run:
```bash
bash installers/install_macos.sh
```

## After install

1. Copy `.env.example` to `.env`.
2. Set `VAULT_PATH`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Optional semantic search settings:
   - `VECTOR_DB=data/vector`
   - `EMBEDDING_MODEL=all-MiniLM-L6-v2`
   - `CHUNK_SIZE=500`
   - `CHUNK_OVERLAP=100`
   - `EMBED_BATCH_SIZE=64`

Then run:

```bash
python main.py --scan
python main.py --index
python main.py --search "insurance renewal"
```
