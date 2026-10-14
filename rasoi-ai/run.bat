@echo off
chcp 65001 > nul
if exist "%USERPROFILE%\.local\bin" (
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
set "PYTHONIOENCODING=utf-8"
echo Starting RasoiAI Backend on http://0.0.0.0:8000 ...
echo Interactive Testbed: http://localhost:8000/test
echo Interactive Docs:    http://localhost:8000/docs
uv run uvicorn src.rasoi_ai.main:app --reload --host 0.0.0.0 --port 8000
