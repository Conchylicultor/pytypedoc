from config_dataclass import *
from chain_dict import *


class Layer(Configurable):
    dim: int


class MyConfig(Configurable):
    x: int = 123
    y: str = "abc"
    name: str = "tpu"
    layer: Layer = Layer()

    model: Layer = field()

    @model.default
    def _(self):
        return self.name


layer = Layer(dim=123)
print(layer)

with as_config():
    layer = Layer(dim=123)
    print(layer)

layer = Layer.config(dim=567)
print(layer)


layer = MyConfig()
print(layer)


config = chain_dict.ChainConfig(
    chain_dict.ConfigDict.from_dict(  # CLI
        {
            "MyConfig.x": 123,
            "MyConfig.y": 123,
        }
    ),
    chain_dict.ConfigDict.from_dict(  # Hyper sweep
        {
            "MyConfig.x": 789,
            "MyConfig.layer.dim": 567,
        }
    ),
    Layer.config(dim=456),
)
root = MyConfig.from_config(config, x=140)
print(root)
