@echo off
title Lucia — Simulation Environment Mode (Isolated / Virtual Time)
cd /d "%~dp0"

echo ===================================================
echo   Launching Lucia Simulation Environment...
echo   [Companion Sleeping / Virtual Clock / In-Memory]
echo ===================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in .venv/
    echo Please run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

cd electron
if not exist "node_modules" (
    echo [INFO] Installing Electron frontend dependencies...
    npm install
)

echo [INFO] Starting Electron in Simulation Mode...
npm run sim
