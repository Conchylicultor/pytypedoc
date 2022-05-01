import builtins
import dataclasses
import collections
from multiprocessing.sharedctypes import Value
from pydoc import resolve
import types
from typing import *

TypeAlias = Any

import bytecode  # import Instr, Bytecode


# **************** Implementation *********************


@dataclasses.dataclass
class ForwardRef:
    name: str
    resolve: Callable[[], Any]

    def __repr__(self):
        return f"ForwardRef({self.name!r})"

    def __getitem__(self, key):
        raise NotImplementedError

    def __getattr__(self, key):
        raise AttributeError


class GlobalAutoResolve(dict):
    def __init__(self, fn):
        self.fn = fn
        code = self.fn.__code__
        if self.fn.__closure__:
            self.closures = dict(zip(self.fn.__code__.co_freevars, self.fn.__closure__))
            code = replace_closure(code)
        else:
            self.closures = {}

        self.globals = collections.ChainMap(
            self.closures,
            self.fn.__globals__,
            builtins.__dict__,
        )
        self.code = code

    def __getitem__(self, key):
        if key in self.closures:
            cell = self.globals[key]
            try:
                return cell.cell_contents
            except ValueError:
                return ForwardRef(name=key, resolve=lambda: cell.cell_contents)
        if key in self.globals:
            return self.globals[key]

        def resolve():
            try:
                return self.globals[key]
            except KeyError:
                raise NameError(key)

        return ForwardRef(name=key, resolve=resolve)


def replace_closure(code):
    instructions = bytecode.Bytecode.from_code(code)
    instructions = bytecode.Bytecode([_replace_closure(inst) for inst in instructions])
    return instructions.to_code()


def _replace_closure(inst):
    if inst.name != "LOAD_DEREF":
        return inst

    return bytecode.Instr(
        name="LOAD_GLOBAL",
        arg=inst.arg.name,
        lineno=inst.lineno,
    )


def type_hints(cls):
    fn = cls.co_annotations
    globs = GlobalAutoResolve(fn)
    hints = eval(globs.code, globs, {})
    print(hints)
    return hints


# **************** Example *********************


@dataclasses.dataclass
class User:
    def co_annotations():
        return {
            "name": str,
            "group": Group,
            "groups": list[Group],
        }


# Get incomplete type hints
incomplete = type_hints(User)


@dataclasses.dataclass
class Group:
    def co_annotations():
        return {
            "name": str,
            "group": list[User],
            "inexisting": DoesNotExists,
        }


def make_cls():
    @dataclasses.dataclass
    class InnerUser:
        def co_annotations():
            return {"name": str, "group": InnerGroup}

    # TODO(epot): Resolve the inner users
    incomplete = type_hints(InnerUser)

    @dataclasses.dataclass
    class InnerGroup:
        def co_annotations():
            return {"name": str, "group": list[InnerUser], "inexisting": DoesNotExists}

    print(incomplete["group"])
    print(incomplete["group"].resolve())
    type_hints(InnerUser)
    return InnerUser, InnerGroup


InnerUser, InnerGroup = make_cls()

type_hints(User)
type_hints(Group)
type_hints(InnerUser)
type_hints(InnerGroup)

print(incomplete["group"])
print(incomplete["group"].resolve())

try:
    type_hints(InnerGroup)["inexisting"].resolve()
except Exception as e:
    print("Exceptiion was correctly raised:", repr(e))
