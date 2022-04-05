"""."""

from typing import Union, Optional

import types_parser


def _validate(t, v):
    pass


def test_validator():

    assert _validate(int, 1)
    assert not _validate(int, "a")

    assert _validate(str, "a")
    assert _validate(str, 1)

    assert _validate(int | str, 1)
    assert _validate(int | str, "a")
    assert _validate(Union[int, str], 1)
    assert _validate(Union[int, str], "a")
    assert not _validate(int | str, None)
    assert not _validate(Union[int, str], None)

    assert _validate(int | str | None, 1)
    assert _validate(int | str | None, "a")
    assert _validate(int | str | None, None)
    assert _validate(Optional[Union[int, str]], None)
    assert not _validate(int | str | None, None)
