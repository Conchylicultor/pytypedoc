"""Reflections."""

from __future__ import annotations

import enum
from typing import Any

from etils import epy
from typedoc import types
from typedoc import utils
import types_parser


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
    TypeLiteral = "Type literal"
    TypeParameter = "Type parameter"
    Variable = enum.auto()


@types_parser.make_dataclass
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


@types_parser.make_dataclass
class SourceReference:
    character: int
    fileName: str
    line: int
    file: str | None = None
    url: str | None = None

    from_json = utils.from_json


@types_parser.make_dataclass
class Comment:
    returns: str | None = None
    shortText: str | None = None
    tags: list[dict[str, str]] | None = None
    text: str | None = None

    from_json = utils.from_json


@types_parser.make_dataclass
class Reflection:
    id: int
    name: str
    kind: ReflectionKind
    sources: list[SourceReference] | None = None
    flags: ReflectionFlags
    comment: Comment | None = None

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
            ReflectionKind.TypeLiteral: DeclarationReflection,
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

        try:
            return cls(**value)
        except Exception as e:
            msg = f'{cls.__name__} ({value["kind"]}): {value["name"]}: {list(value)}'
            epy.reraise(e, prefix="\n" + msg + "\n")


@types_parser.make_dataclass
class ContainerReflection(Reflection):
    children: list[Reflection] | None = None
    categories: Any = None  # Unused
    groups: Any = None  # Unused


@types_parser.make_dataclass
class DeclarationReflection(ContainerReflection):
    signatures: list[SignatureReflection] | None = None
    # Inheritance
    extendedTypes: None | list[types.Type] = None
    # Pointer to overwritten method
    overwrites: None | types.ReferenceType = None
    # Inherited function (not overwritten). Could be skipped
    inheritedFrom: None | types.ReferenceType = None
    type: None | types.Type = None
    indexSignature: SignatureReflection | None = None


@types_parser.make_dataclass
class ReferenceReflection(DeclarationReflection):
    target: int


@types_parser.make_dataclass
class TypeParameterReflection(Reflection):
    type: types.Type = None


@types_parser.make_dataclass
class SignatureReflection(Reflection):
    parameters: list[ParameterReflection] | None = None
    type: types.Type
    overwrites: None | types.ReferenceType = None
    inheritedFrom: None | types.ReferenceType = None
    # Generic, like:
    # addEventListener<T extends E['type']>(type: T, listener: EventListener<E, T, this>): void;
    typeParameter: None | list[TypeParameterReflection] = None


@types_parser.make_dataclass
class ParameterReflection(Reflection):
    type: types.Type | None = None
    # Only used for Enum ?
    defaultValue: str = ""
