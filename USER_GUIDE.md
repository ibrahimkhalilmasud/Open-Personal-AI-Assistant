# USER GUIDE

## 1) Select your vault folder
Open `.env` and set:

```env
VAULT_PATH=/home/user/PersonalVault
```

Examples:
- Windows: `D:\PersonalVault`
- Linux: `/home/user/PersonalVault`
- macOS: `/Users/user/PersonalVault`

Optional scan controls:

```env
AUTO_SCAN=true
SCAN_INTERVAL=300
```

## 2) Run a full scan

```bash
python main.py --scan
```

This recursively scans supported files and updates the database.

## 3) Run live watching

```bash
python main.py --watch
```

This monitors file add/modify/remove events and updates the database automatically.

## 4) Check logs

- `logs/scan.log`
- `logs/watcher.log`
