$env:PYTHONPATH="."
& "C:\Users\juand\Banco\.venv\Scripts\pytest" --cov=application --cov=domain --cov-report=term-missing tests/
