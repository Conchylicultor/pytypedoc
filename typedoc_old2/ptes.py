from __future__ import annotations
import pydantic


class ConfigModel(pydantic.BaseModel):
    pass

    class Config:
        extra = "forbid"
        allow_mutation = False
        smart_union = True


class Foo(ConfigModel):
    sibling: Foo | None = None


foo = Foo(sibling=Foo(x=123, y=234))
print(foo)


# class MyConfig:
#     smart_union = True


# @pydantic.dataclasses.dataclass(config=MyConfig)
# class B:
#     x: int


# @pydantic.dataclasses.dataclass(config=MyConfig)
# class A:
#     x: str | int | None = None
#     a: A = None


# a0 = A(x=1)
# a = A(x=123, a=a0)
# print(type(a.x))
# print(a)
