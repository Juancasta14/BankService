$env:PYTHONPATH="."
$env:DB_PROVIDER="memory"
& "C:\Users\juand\Banco\.venv\Scripts\pytest" --cov=application --cov=domain --cov-report=term-missing tests/
