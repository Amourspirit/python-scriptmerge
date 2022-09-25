def test_coding_re() -> None:
    # https://peps.python.org/pep-0263/
    from stickytape import _RE_CODING

    codings = (
        "# -*- coding: latin-1 -*-",
        "# -*- coding: utf8 -*-",
        "# coding=latin-1",
        "# coding=utf-8",
        "# coding: latin-1",
        "# coding: utf-8",
    )
    for s in codings:
        m = _RE_CODING.match(s)
        assert len(m.groups()) == 1
        

    bad_codings = (
        "# --codeing: latin-1 -*-",
        "# coding utf8",
        "#coding-latin-1",
        "# codin latin-1",
    )
    for s in bad_codings:
        m = _RE_CODING.match(s)
        if m:
            assert len(m.groups()) == 0