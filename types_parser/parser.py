"""Type parser.

Features:

* Validation: `validate(type, value)`


"""

import dataclasses
import enum
import types
import typing
from typing import TypeAlias
from etils import epy
from etils import edc


# Sentinel value
class InvalidError(TypeError):
    pass


def _assert_isinstance(obj, cls):
    if not isinstance(obj, cls):
        raise InvalidError(f"Expected {cls}. Got: {type(obj)}")


def validate(hint: TypeAlias, value):
    origin = typing.get_origin(hint)
    return _ORIGIN_TO_VALIDATOR[origin](hint, value)


def _list_validator(hint: TypeAlias, value):
    (item_hint,) = typing.get_args(hint)
    _assert_isinstance(value, list)
    return [validate(item_hint, val) for val in value]


def _dict_validator(hint: TypeAlias, value):
    key_hint, item_hint = typing.get_args(hint)
    _assert_isinstance(value, dict)
    return {k: validate(item_hint, v) for k, v in value.items()}


def _union_validator(hint: TypeAlias, value):
    item_hints = typing.get_args(hint)
    all_err = []
    for item_hint in item_hints:
        try:  # Return the first valid match
            return validate(item_hint, value)
        except InvalidError as e:
            all_err.append(e)
    else:  # No match
        msg = "\n".join([str(e) for e in all_err])
        raise InvalidError(f"{msg}\nExpected: {hint}. Got: {type(value)}")


def _type_validator(hint: TypeAlias, value):
    if hint is typing.Any:
        return value
    if not isinstance(hint, type):
        raise AssertionError(f"Unsuported typing annotation: {hint}")
    # TODO(epot): Dispatch too
    if issubclass(hint, enum.Enum):
        return hint(value)
    if hasattr(hint, "from_json"):
        if isinstance(value, hint):
            return value
        return hint.from_json(value)
    _assert_isinstance(value, hint)
    return value


_ORIGIN_TO_VALIDATOR = {
    list: _list_validator,
    typing.List: _list_validator,
    # tuple: _tuple_validator,
    # typing.Tuple: _tuple_validator,
    dict: _dict_validator,
    typing.Dict: _dict_validator,
    types.UnionType: _union_validator,
    typing.Union: _union_validator,
    None: _type_validator,
}


@dataclasses.dataclass
class Validator:
    name: str
    hint: TypeAlias

    def __call__(self, value):
        try:
            validate(self.hint, value)
        except Exception as e:
            if isinstance(value, dict):
                input_msg = f"{{{list(value)}}}"
            elif isinstance(value, list):
                input_msg = f"list of {len(value)=}"
            else:
                input_msg = repr(value)
            msg = epy.dedent(
                f"""
                * {self.name}: {self.hint}:
                  * Input: {input_msg}
                """
            )
            epy.reraise(e, prefix="\n" + msg + "\n")


def make_dataclass(cls):
    # Lazyly initialize the class to support forward reference
    def __new__(cls, *args, **kwargs):
        _make_all_dataclass(cls)
        return object.__new__(cls)

    cls.__new__ = __new__
    return cls


def _make_all_dataclass(cls):
    for c in reversed(cls.mro()):
        if c is object:
            continue
        _make_dataclass(c)


def _make_dataclass(cls):
    if "_auto_dc_initialized" in cls.__dict__:
        return
    type_hints = typing.get_type_hints(cls)
    for k, v in type_hints.items():
        validator = Validator(name=f"{cls.__name__}.{k}", hint=v)
        default = getattr(cls, k, dataclasses.MISSING)
        setattr(cls, k, edc.field(validate=validator, default=default))
    cls = dataclasses.dataclass(cls, kw_only=True)
    cls._auto_dc_initialized = True
    return cls
