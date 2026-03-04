import sys
import os
os.environ["PYTHONPATH"] = "."
import pytest

with open("test_log.txt", "w", encoding="utf-8") as f:
    sys.stdout = f
    sys.stderr = f
    pytest.main(['-v', '--tb=short', 'tests/e2e/'])
