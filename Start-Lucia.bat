@echo off
title Lucia — AI Companion Launcher
cd /d "%~dp0"

echo ===================================================
echo   Awakening Lucia — Affective AI Companion...
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

echo [INFO] Launching Lucia Desktop Interface...
npm start
