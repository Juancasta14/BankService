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
    Write-Host "--- DETALLE DE ADVERTENCIAS (WARNINGS) ---" -ForegroundColor Yellow
    Write-Host "Los warnings mostrados arriba no son errores, el codigo funciona perfecto. Solo son avisos de librerias sobre sintaxis que cambiara en versiones futuras:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Pydantic V2 (PydanticDeprecatedSince20):" -ForegroundColor Cyan
    Write-Host "   Pydantic actualizo su sintaxis. En models.py se usa 'class Config:' dentro de los modelos, pero la version nueva de la libreria pide usar 'model_config = ConfigDict(...)'. Se recomiendan actualizar esos modelos a futuro." -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Tiempos (DeprecationWarning de datetime):" -ForegroundColor Cyan
    Write-Host "   En security.py y main.py se usa 'datetime.utcnow()'. Python 3.12+ marco esto como obsoleto porque no guarda la zona horaria adecuadamente. Recomiendan usar 'datetime.now(datetime.UTC)' en proximas refactorizaciones." -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Retorno en Pruebas (PytestReturnNotNoneWarning):" -ForegroundColor Cyan
    Write-Host "   El test 'test_create_pse_payment_success' retorna el 'order_id' como cadena de texto. Pytest advierte que las funciones de test idealmente no deberian retornar valores, solo ejecutar 'asserts'." -ForegroundColor Gray
} else {
    Write-Host "Algunos tests fallaron. Revisa el log de arriba. ❌" -ForegroundColor Red
}
Write-Host "=========================================" -ForegroundColor Cyan

exit $testExitCode
