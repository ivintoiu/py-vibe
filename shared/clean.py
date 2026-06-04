import pathlib
import shutil

for pattern in ["__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"]:
    for path in pathlib.Path(".").rglob(pattern):
        shutil.rmtree(path, ignore_errors=True)

for pattern in ["*.pyc", "*.pyo"]:
    for path in pathlib.Path(".").rglob(pattern):
        path.unlink(missing_ok=True)

shutil.rmtree("htmlcov", ignore_errors=True)
pathlib.Path(".coverage").unlink(missing_ok=True)
