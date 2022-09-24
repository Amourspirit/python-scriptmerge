def test_explicit_relative_imports_drop_module(get_script_str) -> None:
    script: str = get_script_str("explicit_relative_import/hello")
    assert script.find("Hello") > 0

    script = get_script_str("explicit_relative_import/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1


def test_from_as_module_drop(get_script_str) -> None:
    script: str = get_script_str("import_from_as_module/hello")
    assert script.find("Hello") > 0

    script = get_script_str("import_from_as_module/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1


def test_import_as_value_drop(get_script_str) -> None:
    script: str = get_script_str("import_from_as_value/hello")
    assert script.find("Hello") > 0

    script = get_script_str("import_from_as_value/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1


def test_imports_in_imported_modules_drop(get_script_str) -> None:
    script: str = get_script_str("imports_in_imported_modules/hello")
    assert script.find("Hello") > 0

    script = get_script_str("imports_in_imported_modules/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1


def test_script_using_from_to_import_module_drop(get_script_str) -> None:
    script: str = get_script_str("script_using_from_to_import_module/hello")
    assert script.find("Hello") > 0

    script = get_script_str("script_using_from_to_import_module/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1


def test_script_using_from_to_import_multiple_modules_drop(get_script_str) -> None:
    script: str = get_script_str("script_using_from_to_import_multiple_modules/hello")
    assert script.find("Hello") > 0

    script = get_script_str(
        "script_using_from_to_import_multiple_modules/hello", exclude_python_modules=["greetings*"]
    )
    assert script.find("Hello") == -1


def test_script_using_from_to_import_multiple_values_drop(get_script_str) -> None:
    script: str = get_script_str("script_using_from_to_import_multiple_values/hello")
    assert script.find("Hello") > 0

    script = get_script_str("script_using_from_to_import_multiple_values/hello", exclude_python_modules=["greeting*"])
    assert script.find("Hello") == -1


def test_script_using_stdlib_module_in_package_drop(get_script_str) -> None:
    script: str = get_script_str("script_using_stdlib_module_in_package/hello")
    assert script.find("Hello") > 0

    script = get_script_str("script_using_stdlib_module_in_package/hello", exclude_python_modules=["greeting*"])
    assert script.find("Hello") == -1


def test_script_with_single_local_import_drop(get_script_str) -> None:
    script: str = get_script_str("script_with_single_local_import/hello")
    assert script.find("Hello") > 0

    script = get_script_str("script_with_single_local_import/hello", exclude_python_modules=["greeting*"])
    assert script.find("Hello") == -1


def test_script_with_single_local_import_drop(get_script_str) -> None:
    script: str = get_script_str("script_using_multi_import/hello")
    assert script.find("Hello") > 0
    assert script.find("Goodbye") > 0

    script = get_script_str("script_using_multi_import/hello", exclude_python_modules=["greetings*"])
    assert script.find("Hello") == -1
    assert script.find("Goodbye") == -1
