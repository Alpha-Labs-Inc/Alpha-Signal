import json


def load_config(file_path: str, model):
    with open(file_path, "r") as file:
        data = json.load(file)
    return model(**data)
