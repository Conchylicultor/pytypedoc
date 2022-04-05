from __future__ import annotations

import dataclasses
import enum
import functools

from etils import edc
from etils import epy

from typedoc import utils


@dataclasses.dataclass(kw_only=True)
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


@dataclasses.dataclass(kw_only=True)
class ArrayType(Type):
    elementType: Type = edc.field(validate=Type.from_json)


@dataclasses.dataclass(kw_only=True)
class IntrinsicType(Type):
    name: str


@dataclasses.dataclass(kw_only=True)
class LiteralType(Type):
    value: str | None | int | float | bool


@dataclasses.dataclass(kw_only=True)
class ReferenceType(Type):
    """Reference can be.

    Internal: `id` is set
    External: `package` & `qualifiedName` set
    """

    id: int | None = None
    name: str
    qualifiedName: str = None
    package: str = None
    # Used
    typeArguments: Type = utils.field_list(Type)


@dataclasses.dataclass(kw_only=True)
class ReflectionType(Type):
    """Example: callback.

    onError: (message: string) => void
    """

    declaration: str = None


@dataclasses.dataclass(kw_only=True)
class UnionType(Type):
    types: list[Type] = edc.field(
        validate=lambda vals: [Type.from_json(v) for v in vals]
    )


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
