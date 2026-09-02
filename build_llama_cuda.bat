@echo off
echo === Installing llama-cpp-python with CUDA Support ===
echo.

set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6
set PATH=%CUDA_PATH%\bin;%PATH%

echo Installing prebuilt CUDA 12.4+ wheel (compatible with CUDA 12.6+)...
.venv\Scripts\pip.exe install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --force-reinstall --no-cache-dir

echo.
echo === Verifying Installation ===
.venv\Scripts\python.exe -c "import llama_cpp; print('llama_cpp version:', llama_cpp.__version__); print('GPU acceleration available:', llama_cpp.llama_supports_gpu_offload())"

echo.
echo === Done. Exit code: %ERRORLEVEL% ===
