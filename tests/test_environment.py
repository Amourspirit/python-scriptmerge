import os


def test_environment() -> None:
    import scriptmerge

    env_var = os.environ.get("SCRIPT_MERGE_ENVIRONMENT", None)
    assert env_var == "1"
