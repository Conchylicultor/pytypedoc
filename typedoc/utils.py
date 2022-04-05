"""Utils."""

from __future__ import annotations

import dataclasses
import enum
import functools

from etils import edc
from etils import epy
from typing_extensions import Self
from typedoc import utils


@classmethod
def from_json(cls, value) -> Self:
    if isinstance(value, dict):
        return cls(**value)
    elif isinstance(value, cls):
        return value
    elif value is None:
        return value
    else:
        raise TypeError(f"{cls.__name__} got unexpected: {type(value)}")


def field_list(cls, print_: bool = False):
    def _make_list(vals):
        if vals is None:
            return None
        return [cls.from_json(v) for v in vals]

    if print_:
        _make_list = utils.print_field(_make_list)

    return edc.field(
        default=None,
        validate=_make_list,
    )


def print_field(fn, prefix: str = ""):
    def new_fn(val):
        print(prefix, val)
        return fn(val)

    return new_fn
