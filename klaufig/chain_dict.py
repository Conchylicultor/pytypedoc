"""Config."""

import dataclasses
from typing import Any

from etils import epy


class Resolver:
    pass


class CliResolver(Resolver):
    pass


class ProxyResolver(Resolver):
    pass


class ConfigPath:
    # TODO: Should also keep track of the source
    pass


@dataclasses.dataclass
class ConfigItem:
    def build(self):
        pass


@dataclasses.dataclass
class ResolvedItem:
    path: ConfigPath
    value: Any
    dependencies: list[ConfigPath]


class BaseConfig:
    """.

    Attributes:
        path: Path
        origin: Information on where the config value comes from (file, CLI,...)
        resolved: Keep track of the resolved values, with the dependency chain
    """

    path: ConfigPath = None
    origin: str = "Unkown"
    resolved: dict[str, ResolvedItem] = dataclasses.field(default_factory=dict)

    def get(self, key, default):
        raise NotImplementedError(f"{type(self).__qualname__}.get")


@dataclasses.dataclass
class ConfigDict(BaseConfig):
    vals: Any = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, d, **kwargs):
        assert not kwargs
        return cls(vals=d)

    def __repr__(self) -> str:
        lines = epy.Lines()
        lines += f"{self.__class__.__qualname__}("
        with lines.indent():
            for k, v in self.vals.items():
                lines += f"{k}={v!r}"
        lines += ")"
        return lines.join(collapse=not bool(self.vals))


missing = object()


class ChainConfig(BaseConfig):
    def __init__(self, *configs):
        # TODO: Insert an empty ConfigDict for insert values ?
        self.configs = configs  # (ConfigDict(), *configs)

    def __getitem__(self, key):
        for conf in self.configs:
            if (value := conf.get(key, missing)) != missing:
                # TODO: Keep track of the value (in resolved)
                return value
        raise KeyError(key)

    def __repr__(self) -> str:
        lines = epy.Lines()
        lines += f"{self.__class__.__qualname__}("
        with lines.indent():
            for conf in self.configs:
                lines += f"{conf!r},"
        lines += ")"
        return lines.join()

    def make(self, cls):
        """."""
        # How to handle conflict & collisions ?
        root_path = ConfigPath(cls.__name__)
