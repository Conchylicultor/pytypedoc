"""Reflections."""

from __future__ import annotations

import dataclasses
from email.policy import default
import enum
import functools
from typing import Type

from etils import edc
from etils import epy
from typedoc import types
from typedoc import utils


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


@dataclasses.dataclass(kw_only=True)
class ReflectionFlags:
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

    from_json = utils.from_json


@dataclasses.dataclass(kw_only=True)
class SourceReference:
    character: int
    fileName: str
    line: int
    file: str | None = None
    url: str | None = None

    from_json = utils.from_json


@dataclasses.dataclass(kw_only=True)
class Reflection:
    id: int
    name: str
    kind: ReflectionKind
    sources: list[SourceReference] = utils.field_list(SourceReference)
    flags: ReflectionFlags = edc.field(validate=ReflectionFlags.from_json)
    comment: str | None = None

    @classmethod
    def from_json(cls, value) -> Reflection:
        value = dict(value)
        value.pop("kind")
        value["kind"] = ReflectionKind(value.pop("kindString"))
        kind_to_cls = {
            ReflectionKind.Reference: ReferenceReflection,
            ReflectionKind.Project: ContainerReflection,
            ReflectionKind.Namespace: ContainerReflection,
            ReflectionKind.Enum: ContainerReflection,
            ReflectionKind.Class: DeclarationReflection,
            ReflectionKind.Function: DeclarationReflection,
            ReflectionKind.Method: DeclarationReflection,
            ReflectionKind.Constructor: DeclarationReflection,
            ReflectionKind.Property: DeclarationReflection,
            ReflectionKind.CallSignature: SignatureReflection,
            ReflectionKind.ConstructorSignature: SignatureReflection,
            ReflectionKind.Parameter: ParameterReflection,
            ReflectionKind.Variable: ParameterReflection,
            ReflectionKind.EnumMember: ParameterReflection,
            ReflectionKind.TypeParameter: TypeParameterReflection,
        }
        cls = kind_to_cls.get(value["kind"], Reflection)
        cls.update_init_kwargs(value)

        try:
            return cls(**value)
        except Exception as e:
            print(e)
            print()
            print(f'{cls.__name__} ({value["kind"]}): {value["name"]}: {list(value)}')
            raise

    @classmethod
    def update_init_kwargs(cls, value) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class ContainerReflection(Reflection):
    children: list[Reflection] | None = utils.field_list(Reflection)

    @classmethod
    def update_init_kwargs(cls, value) -> None:
        super().update_init_kwargs(value)
        value.pop("categories", None)  # Groups can be dynamically computed
        value.pop("groups", None)  # Groups can be dynamically computed


@dataclasses.dataclass(kw_only=True)
class DeclarationReflection(ContainerReflection):
    signatures: list[SignatureReflection] | None = utils.field_list(Reflection)
    # Inheritance
    extendedTypes: list[Type] = utils.field_list(types.Type)
    # Pointer to overwritten method
    overwrites: None | types.ReferenceType = edc.field(
        validate=types.ReferenceType.from_json, default=None
    )
    # Inherited function (not overwritten). Could be skipped
    inheritedFrom: None | types.ReferenceType = edc.field(
        validate=types.ReferenceType.from_json, default=None
    )
    type: types.Type = edc.field(validate=types.Type.from_json, default=None)


@dataclasses.dataclass(kw_only=True)
class ReferenceReflection(DeclarationReflection):
    target: int


@dataclasses.dataclass(kw_only=True)
class TypeParameterReflection(Reflection):
    type: types.Type = edc.field(validate=types.Type.from_json, default=None)


@dataclasses.dataclass(kw_only=True)
class SignatureReflection(Reflection):
    parameters: list[ParameterReflection] | None = utils.field_list(Reflection)
    type: types.Type = edc.field(validate=types.Type.from_json)
    overwrites: None | types.ReferenceType = edc.field(
        validate=types.ReferenceType.from_json, default=None
    )
    inheritedFrom: None | types.ReferenceType = edc.field(
        validate=types.ReferenceType.from_json, default=None
    )
    # Generic, like:
    # addEventListener<T extends E['type']>(type: T, listener: EventListener<E, T, this>): void;
    typeParameter: list[TypeParameterReflection] = utils.field_list(
        TypeParameterReflection
    )


@dataclasses.dataclass(kw_only=True)
class ParameterReflection(Reflection):
    type: types.Type = edc.field(validate=types.Type.from_json, default=None)
    # Only used for Enum ?
    defaultValue: int = edc.field(validate=int, default=-1)
