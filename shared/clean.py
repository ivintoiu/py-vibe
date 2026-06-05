import pathlib
import shutil


def clean_build_artifacts():
    # Clean Python cache and build artifact directories
    for pattern in ["__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "*.egg-info"]:
        for path in pathlib.Path(".").rglob(pattern):
            try:
                shutil.rmtree(path)
            except (OSError, PermissionError):
                pass

    # Clean compiled Python bytecode files
    for pattern in ["*.pyc", "*.pyo"]:
        for path in pathlib.Path(".").rglob(pattern):
            path.unlink(missing_ok=True)

    # Clean coverage reports
    try:
        shutil.rmtree("htmlcov")
    except (FileNotFoundError, OSError, PermissionError):
        pass

    pathlib.Path(".coverage").unlink(missing_ok=True)


if __name__ == "__main__":
    clean_build_artifacts()
