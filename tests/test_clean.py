def test_script_using_multi_import_clean(get_script_str) -> None:
    script: str = get_script_str("script_using_multi_import/hello")
    assert script.find("# Message for greeting") > 0
    assert script.find("# Message for negelect") > 0

    script: str = get_script_str("script_using_multi_import/hello", clean=True)
    assert script.find("Hello") > 0
    assert script.find("Goodbye") > 0
    assert script.find("# Message for greeting") == -1
    assert script.find("# Message for negelect") == -1
    
def test_script_import_class(get_script_str) -> None:
    script: str = get_script_str("script_import_class/hello")
    assert script is not None
    
    script: str = get_script_str("script_import_class/hello", clean=True)
    assert script is not None