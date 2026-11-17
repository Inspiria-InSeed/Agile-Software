# Inseed

Inseed is a self-hosted project and issue tracker with a Kanban board, project
spaces, assignees, priorities, comments, and local account sign-in. It uses
SQLite by default and does not require a paid service or external frontend.

## Run locally on Windows

From the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open <http://127.0.0.1:8001/> and create the first account. The application
creates `inseed_db.db` in the project directory and initializes an `INSEED`
project automatically. Set `SECRET_KEY` in the environment or a local `.env`
file to keep sessions valid across server restarts; otherwise, a random key is
generated each time the app starts. Keep the server bound to `127.0.0.1` for
local-only access.

## Run as a Windows service

Install NSSM for the current Windows user, then run this from PowerShell in the
project directory:

```powershell
winget install --id NSSM.NSSM --scope user
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_inseed_service.ps1
```

The installer requests administrator approval, sets the service to start
automatically with Windows, and runs it as the restricted LocalService account.
The service can run without VS Code open, as long as the computer is on. It
receives read/execute access to the project and Python directories and write
access to its data and log directories under `C:\ProgramData\InseedService`.
The installer preserves the project database under
`C:\ProgramData\InseedService\data` and writes service logs under
`C:\ProgramData\InseedService\logs`. It creates a private `.env` secret if one
does not exist. To repair or replace an existing installation, add
`-RepairExisting` to the installer command. Check or control the service with:

```powershell
Get-Service Inseed
Start-Service Inseed
Stop-Service Inseed
```
