"""Check real imports plus meaningful failure paths, without market records."""
from src.validate_environment import REQUIRED_MODULES, validate_environment


def test_actual_environment():
    results, success = validate_environment()
    assert success, "\n".join(results)


def test_missing_dependency_is_reported_and_checks_continue():
    seen = []
    def importer(name):
        seen.append(name)
        if name == "pandas":
            raise ModuleNotFoundError("dependency unavailable")
    results, success = validate_environment(importer, lambda name: "test", (3, 12))
    assert not success
    assert any("FAIL pandas: ModuleNotFoundError" in line for line in results)
    assert seen == list(REQUIRED_MODULES)
    assert any("PASS pytest" in line for line in results)


def test_incompatible_python_is_reported():
    results, success = validate_environment(lambda name: None, lambda name: "test", (3, 11))
    assert not success
    assert results[0].startswith("FAIL Python 3.11")


def test_broken_import_is_reported():
    def importer(name):
        raise RuntimeError("binary incompatibility")
    results, success = validate_environment(importer, lambda name: "test", (3, 12))
    assert not success
    assert any("RuntimeError: binary incompatibility" in line for line in results)
