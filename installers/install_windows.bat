@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
echo Installation complete. Run: python main.py
