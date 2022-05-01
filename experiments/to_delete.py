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

# TODO(epot): Slots


class MyException0(Exception):
    pass
    # def __init__(self, a):
    #     pass


def fn():
    raise ImportError(123, 567, path="asdsa")


def reraise(e):
    class MyException(type(e)):
        def __str__(self):
            return "Additional message"

    # e.__str__ = lambda x: 'asdas'
    print(list(e.__dict__))
    print(dir(e))
    try:
        e.__class__ = MyException
    except TypeError:
        pass
    else:
        raise

    if type(e).__str__ == Exception.__str__:
        e.args = (f"Additional message: {str(e)}",)
        raise

    print(type(e).__str__)
    print(Exception.__str__)
    raise ValueError(
        "Unexpected exception",
    )


import builtins

ers = [v for v in dir(builtins) if v.endswith(("Error", "Exception"))]
# print("\n".join(ers))

print("*****")
for e in ers:
    if getattr(builtins, e).__str__ != Exception.__str__:
        print(e, "<<")
    else:
        print(e)

# try:
#     fn()
# except Exception as e:
#     reraise(e)
