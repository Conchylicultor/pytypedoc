"""Reflextion."""


from __future__ import annotations

import dataclasses
import enum
import functools
from typing import Type

from etils import edc
from etils import epy
import pydantic


class ReflectionKind(epy.StrEnum):
    def _generate_next_value_(
        name, start, count, last_values
    ) -> str:  # pylint: disable=no-self-argument
        return name

    Accessor = enum.auto()
    CallSignature = "Call signature"
    Class = enum.auto()
    Constructor = enum.auto()
    ConstructorSignature = "Constructor signature"
    Enum = "Enumeration"
    EnumMember = "Enumeration member"
    Event = enum.auto()
    Function = enum.auto()
    GetSignature = enum.auto()
    IndexSignature = enum.auto()
    Interface = enum.auto()
    Method = enum.auto()
    Module = enum.auto()
    Namespace = enum.auto()
    ObjectLiteral = enum.auto()
    Parameter = enum.auto()
    Project = enum.auto()
    Property = enum.auto()
    Reference = enum.auto()
    SetSignature = enum.auto()
    TypeAlias = enum.auto()
    TypeLiteral = enum.auto()
    TypeParameter = "Type parameter"
    Variable = enum.auto()


class ReflectionFlags(pydantic.BaseModel):
    hasExportAssignment: bool = False
    isAbstract: bool = False
    isConst: bool = False
    isExternal: bool = False
    isOptional: bool = False
    isPrivate: bool = False
    isProtected: bool = False
    isPublic: bool = False
    isReadonly: bool = False
    isRest: bool = False
    isStatic: bool = False
