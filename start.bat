@echo off
start "CrisisMind Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
start "CrisisMind Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
