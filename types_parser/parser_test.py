"""."""

from __future__ import annotations

import dataclasses
import enum
from typing import List, Optional, Union
import typing

import pytest
import types_parser


missing = object()


class MyEnum(enum.Enum):
    A = "a"
    B = 123


def _validate(t, v, expected=missing):
    if expected is missing:
        expected = v
    assert types_parser.validate(t, v) == expected


def _invalid_validate(t, v):
    with pytest.raises(types_parser.InvalidError):
        types_parser.validate(t, v)


@dataclasses.dataclass(eq=True)
class MyClass:
    x: int

    @classmethod
    def from_json(cls, value):
        return cls(**value)


def test_validator():

    _validate(int, 1)
    _invalid_validate(int, "a")

    _validate(str, "a")
    _invalid_validate(str, 1)

    _validate(int | str, 1)
    _validate(int | str, "a")
    _validate(Union[int, str], 1)
    _validate(Union[int, str], "a")
    _invalid_validate(int | str, None)
    _invalid_validate(Union[int, str], None)

    _validate(int | str | None, 1)
    _validate(int | str | None, "a")
    _validate(int | str | None, None)
    _validate(Optional[Union[int, str]], None)
    _invalid_validate(int | str | None, 1.0)

    _validate(List[int], [])
    _validate(list[int], [])
    _validate(List[int], [1, 2, 3])
    _validate(list[int], [1, 2, 3])
    _invalid_validate(List[int], None)
    _invalid_validate(list[int], None)
    _invalid_validate(List[int], [1, 2, "a", 3])
    _invalid_validate(list[int], [1, 2, "a", 3])

    _validate(Optional[List[int]], None)
    _validate(Optional[list[int]], None)
    _validate(Optional[List[int]], [])
    _validate(Optional[list[int]], [])
    _validate(Optional[List[int]], [1, 2, 3])
    _validate(Optional[list[int]], [1, 2, 3])
    _invalid_validate(Optional[List[int]], [1, 2, "a", 3])
    _invalid_validate(Optional[list[int]], [1, 2, "a", 3])
    _validate(Optional[list[int | str]], [1, 2, "a", 3])

    _validate(list[MyClass] | None, None)
    _validate(list[MyClass] | None, [])
    _validate(list[MyClass] | None, [MyClass(x=3)])
    _validate(list[MyClass] | None, [dict(x=3)], [MyClass(x=3)])

    _validate(MyEnum, MyEnum.A)
    _validate(MyEnum, "a", MyEnum.A)


@types_parser.make_dataclass
class MyDataclass:
    x: int = 0
    y: None | list[MyDataclass] = None


@types_parser.make_dataclass
class MyDataclass2(MyDataclass):
    z: str = "def"


def test_cls():
    a = MyDataclass()
    a2 = MyDataclass(x=4)
    assert a.x == 0
    assert a.y is None
    assert a2.x == 4
    assert a2.y is None
    with pytest.raises(types_parser.InvalidError):
        MyDataclass(x="4")

    MyDataclass2(z="abc")
