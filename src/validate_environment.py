"""Validate Python and required imports without reading or creating market data."""
from importlib import import_module
from importlib.metadata import version
import sys

REQUIRED_MODULES = {
    "pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
    "seaborn": "seaborn", "plotly": "plotly", "jupyter": "jupyter",
    "jupyterlab": "jupyterlab", "ipykernel": "ipykernel",
    "openpyxl": "openpyxl", "xlsxwriter": "xlsxwriter", "pytest": "pytest",
    "arabic_reshaper": "arabic-reshaper", "bidi": "python-bidi",
    "streamlit": "streamlit",
}


def validate_environment(importer=import_module, version_reader=version, python_version=None):
    """Return readable check results and overall success; import failures are explicit."""
    current = sys.version_info[:2] if python_version is None else python_version
    success = tuple(current) == (3, 12)
    results = [f"{'PASS' if success else 'FAIL'} Python {current[0]}.{current[1]} (required: 3.12)"]
    for module, distribution in REQUIRED_MODULES.items():
        try:
            importer(module)
            installed = version_reader(distribution)
        except Exception as exc:
            success = False
            results.append(f"FAIL {distribution}: {type(exc).__name__}: {exc}")
        else:
            results.append(f"PASS {distribution} {installed}")
    return results, success


def main():
    results, success = validate_environment()
    print("\n".join(results))
    print("Environment validation: " + ("PASS" if success else "FAIL"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
