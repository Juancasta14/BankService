$env:PYTHONPATH="."
pytest --cov=application --cov=domain --cov-report=term-missing tests/
