import json
import typedoc


def test_api():
    with open("api.json") as f:
        api_json = json.load(f)

    api_container = typedoc.Reflection.from_json(api_json)
    api_container.save_as_python("python/")
