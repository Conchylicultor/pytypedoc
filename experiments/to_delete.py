""".

Reraise an exception with additional informations

Customizing an exception message by adding additional info is extremely common (see 4.2 for thoushands of examples of `e.args += `).

Easy way to add notes to exceptions while controling the formatting.

Issue:

Currently, there is no easy way of reraising an exception

Why is it important ?

* Clearer error messages
*

None of the alternative are satisfying as they all have limitations.

Existing options:

1) Using `e.add_note` and `e.__notes__` (PEP ...)
2) Using `raise ... from e`
3) Mocking the traceback rendering (e.g. registering a `sys.excepthook`)
4) Using hacks to modify the exception in-place
4.1) Mutating the exception `e.args += (msg + str(e),)`
4.2)

Mocking the raise statement ?

"""

from typing import Type


import builtins
import functools


class A:
    x = 1
    y = 2


# err =
# err.args = (f'ddd{err}',)
# # print('>>', str(err), repr(err))
# raise err


@functools.lru_cache(None)
def _all_builtin_exc_cls() -> set[Exception]:
    # Note: We do not support BaseException on purpose
    # TODO(py311): Support ExceptionGroup
    all_exc_cls = []
    for v in dir(builtins):
        if not (v.endswith("Error") or v == "Exception"):
            continue
        exc_cls = getattr(builtins, v)
        assert isinstance(exc_cls, type) and issubclass(exc_cls, Exception)
        all_exc_cls.append(exc_cls)
    return set(all_exc_cls)


def reraise(e):
    msg = f"<<<{e}>>>"

    exc_cls = type(e)

    # 1st case: builtins
    print(exc_cls)
    print(_all_builtin_exc_cls())
    if exc_cls in _all_builtin_exc_cls():
        exc_cls.args = (msg,)
        raise

    # 2nd case: User-defined exception
    class MyException(type(e)):
        def __str__(self):
            return msg

    # print(list(e.__dict__))
    # print(dir(e))
    try:
        e.__class__ = MyException
    except TypeError:
        pass
    else:
        raise

    # 3rd case: Unsuported exception
    # Not sure if there is actually a use-case. Maybe for C++
    # defined exceptions.
    raise NotImplementedError("Unsuported")


class MyException0(Exception):
    pass


class MyException1(Exception):
    __slots__ = ()
    # def __init__(self, a):
    #     pass


exc_to_try = [
    MyException0,
    MyException1,
    ValueError,
    ValueError("asdasd"),
    ValueError("asdasd", "rtyrt"),
    AttributeError("asdas", name="y2", obj=A),
    ImportError(123, 567, path="asdsa"),
]

for exc in exc_to_try:
    try:
        try:
            raise exc
        except Exception as e:
            reraise(e)
    except Exception as e:
        print(repr(e), str(e))
