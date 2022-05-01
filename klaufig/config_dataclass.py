"""."""

from __future__ import annotations

from typing import Any
import dataclasses
import contextlib

from etils import epy
import chain_dict

# from klaufig import chain_dict

is_config = False
ctx = None


@contextlib.contextmanager
def as_config():
    global is_config
    try:
        is_config = True
        yield
    finally:
        is_config = False


@contextlib.contextmanager
def config_context(config):
    global ctx
    try:
        ctx = config
        yield
    finally:
        ctx = None


@dataclasses.dataclass
class ConfigProxy(chain_dict.BaseConfig):
    wrapped_cls: Any
    kwargs: Any

    def __repr__(self) -> str:
        lines = epy.Lines()
        lines += f"{self.__class__.__qualname__}({self.wrapped_cls.__qualname__}("
        with lines.indent():
            for k, v in self.kwargs.items():
                lines += f"{k}={v!r}"
        lines += "))"
        return lines.join(collapse=not bool(self.kwargs))


@dataclasses.dataclass
class DefaultConfig(chain_dict.BaseConfig):
    wrapped_cls: Any


class ConfigMeta(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        global is_config
        is_config = True
        return super().__prepare__(name, bases, **kwds)

    def __new__(cls, name, bases, classdict):
        global is_config
        is_config = False

        return super().__new__(cls, name, bases, classdict)


class Configurable(metaclass=ConfigMeta):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dataclasses.dataclass(cls)

        original_init = cls.__init__

        # Custom init which choose whether to construct the object with or without config
        def __init__(self, **kwargs):
            if config := self._with_config:
                assert not kwargs
                # TODO: Resolve kwargs
                # TODO: Should keep track of the parent config too
                print(config)
                # Inject all values
                # TODO(epot): Conflict with dataclass default factory & cie !!

                kwargs = {
                    f.name: config[f.name].build() for f in dataclasses.fields(self)
                }
                original_init(self, **kwargs)
            else:
                # TODO: Save
                original_init(self, **kwargs)

        cls.__init__ = __init__

    def __new__(cls, **kwargs):
        if is_config:
            return ConfigProxy(cls, kwargs)

        self = super().__new__(cls)
        if ctx is None:  # Constructed without config (use default)
            # TODO(epot): Could patch the init now to overwrite
            self._with_config = None
        else:
            assert not kwargs
            self._with_config = ctx
        return self

    @classmethod
    def config(cls, **kwargs):
        return ConfigProxy(cls, kwargs)

    @classmethod
    def from_config(cls, config, **kwargs):
        overwrite_config = ConfigProxy(cls, kwargs)
        # Might not be the right place to add default (should add in __new__ or __init__ ?)
        default_config = DefaultConfig(cls)
        merged_config = chain_dict.ChainConfig(overwrite_config, config, default_config)
        assert not is_config
        # TODO: Finalize the config (initialize the tracking of:
        # * Which param is unused
        # * Which values are used
        with config_context(merged_config):
            return cls()


class field:
    def __init__(self) -> None:
        self._default_fn = None

    def __set_name__(self, owner, name):
        self._owner = owner
        self._name = name

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return getattr(obj, self._obj_name)

    def __set__(self, obj, value):
        if isinstance(value, field):  # Dataclass `__init__` think `field` is default
            value = self._default_fn(obj)
        setattr(obj, self._obj_name, value)

    @property
    def _obj_name(self):
        return f"_gg_{self._name}"

    # TODO(epot): Making the descriptor default being applied when
    # config is not applied
    def default(self, fn):
        self._default_fn = fn
        return fn
