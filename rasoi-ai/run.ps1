# Startup script for RasoiAI Backend
if (Test-Path "$env:USERPROFILE\.local\bin") {
    $env:Path = "$env:USERPROFILE\.local\bin;" + $env:Path
}
$env:PYTHONIOENCODING = "utf-8"
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Starting RasoiAI Backend on http://0.0.0.0:8000 ...     " -ForegroundColor Green
Write-Host "  Interactive Visual Testbed: http://localhost:8000/test   " -ForegroundColor Cyan
Write-Host "  Interactive Swagger Docs:   http://localhost:8000/docs   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green

uv run uvicorn src.rasoi_ai.main:app --reload --host 0.0.0.0 --port 8000
