<#
.SYNOPSIS
Script para ejecutar toda la suite de pruebas del backend (app_fastapi) con cobertura.

.DESCRIPTION
Este script configura automáticamente el PYTHONPATH necesario, activa el entorno virtual
y ejecuta pytest generando un reporte de cobertura en la terminal.
#>

$ErrorActionPreference = "Stop"

# Directorio raíz del repositorio BankService
$BasePath = Resolve-Path "$PSScriptRoot"
$AppPath = Join-Path $BasePath "App\fastapi_app"
$VenvActivate = Join-Path $AppPath "venv\Scripts\Activate.ps1"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Iniciando Suite de Pruebas de BankService" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Configurar PYTHONPATH
$env:PYTHONPATH = $BasePath
Write-Host "[OK] PYTHONPATH configurado a: $env:PYTHONPATH" -ForegroundColor Green

# 2. Activar Entorno Virtual
if (Test-Path $VenvActivate) {
    Write-Host "[OK] Entorno virtual encontrado. Activando..." -ForegroundColor Green
    & $VenvActivate
} else {
    Write-Host "[ERROR] No se encontró el entorno virtual en $AppPath\venv" -ForegroundColor Red
    Write-Host "Por favor, crea el entorno e instala las dependencias primero." -ForegroundColor Yellow
    exit 1
}

# 3. Ejecutar Pytest
Write-Host "`nEjecutando pytest..." -ForegroundColor Cyan
Set-Location $BasePath
pytest App/fastapi_app/tests/ --cov=App.fastapi_app --cov-report=term-missing

$testExitCode = $LASTEXITCODE

# 4. Finalizar
Write-Host "`n=========================================" -ForegroundColor Cyan
if ($testExitCode -eq 0) {
    Write-Host "¡Todos los tests pasaron exitosamente! 🎉" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nota sobre las advertencias (Warnings):" -ForegroundColor Yellow
    Write-Host "- Pydantic V2: Pide usar 'model_config' en lugar de 'class Config:'." -ForegroundColor Gray
    Write-Host "- Datetime: 'datetime.utcnow()' está obsoleto, recomienda 'datetime.now(datetime.UTC)'." -ForegroundColor Gray
    Write-Host "- Pytest return: Advierte que un test está devolviendo un valor (order_id) en vez de None." -ForegroundColor Gray
} else {
    Write-Host "Algunos tests fallaron. Revisa el log de arriba. ❌" -ForegroundColor Red
}
Write-Host "=========================================" -ForegroundColor Cyan

exit $testExitCode
