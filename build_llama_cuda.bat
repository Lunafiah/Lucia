@echo off
echo === Activating VS 2022 Build Tools (x64) ===
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

echo.
echo === Setting CUDA + Ninja build flags ===

set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6
set PATH=%CUDA_PATH%\bin;C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;%PATH%

rem Use Ninja generator to bypass VS CUDA toolset detection issue with VS v18
rem -DCMAKE_CUDA_COMPILER forces nvcc to be found directly
set CMAKE_ARGS=-DGGML_CUDA=on -DCMAKE_GENERATOR=Ninja -DCMAKE_CUDA_COMPILER="%CUDA_PATH%\bin\nvcc.exe" -DCMAKE_C_COMPILER=cl -DCMAKE_CXX_COMPILER=cl

echo CMAKE_ARGS=%CMAKE_ARGS%
echo CUDA_PATH=%CUDA_PATH%

echo.
echo === Building llama-cpp-python with CUDA (Ninja generator) ===
echo This will take 5-15 minutes. Please wait...
echo.

.venv\Scripts\pip.exe install llama-cpp-python --force-reinstall --no-cache-dir

echo.
echo === Build complete. Exit code: %ERRORLEVEL% ===
