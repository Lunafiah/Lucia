@echo off
title Lucia — UI Standalone Preview Mode (0% VRAM / Brain Sleeping)
cd /d "%~dp0"

echo ===================================================
echo   Opening Lucia UI Preview (Offline / Mock Mode)...
echo   [Python backend and LLM model are NOT activated]
echo ===================================================

cd electron
if not exist "node_modules" (
    echo [INFO] Installing Electron frontend dependencies...
    npm install
)

npm run preview
