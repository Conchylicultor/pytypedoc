from __future__ import annotations

import dataclasses
import enum
import functools

from etils import epy

from typedoc import utils
from typedoc import reflections
import types_parser


@types_parser.make_dataclass
class Type:
    type: str

    @classmethod
    def from_json(cls, val):
        if val is None:
            return None
        cls = TypeKindMap[val["type"]]
        try:
            return cls(**val)
        except Exception as e:
            print(e)
            print(val)
            raise


@types_parser.make_dataclass
class ArrayType(Type):
    elementType: Type


@types_parser.make_dataclass
class IntrinsicType(Type):
    name: str


@types_parser.make_dataclass
class LiteralType(Type):
    value: str | None | int | float | bool


@types_parser.make_dataclass
class ReferenceType(Type):
    """Reference can be.

    Internal: `id` is set
    External: `package` & `qualifiedName` set
    """

    id: int | None = None
    name: str
    qualifiedName: str | None = None
    package: str | None = None
    # Used
    typeArguments: None | list[Type] = None


@types_parser.make_dataclass
class ReflectionType(Type):
    """Example: callback.

    onError: (message: string) => void
    """

    declaration: reflections.DeclarationReflection | None = None


@types_parser.make_dataclass
class UnionType(Type):
    types: list[Type]


TypeKindMap = {
    "array": ArrayType,
    "conditional": None,
    "indexedAccess": None,
    "inferred": None,
    "intersection": None,
    "intrinsic": IntrinsicType,
    "literal": LiteralType,
    "mapped": None,
    "named-tuple-member": None,
    "optional": None,
    "predicate": None,
    "query": None,
    "reference": ReferenceType,
    "reflection": ReflectionType,
    "rest": None,
    "template-literal": None,
    "tuple": None,
    "typeOperator": None,
    "union": UnionType,
    "unknown": None,
}
