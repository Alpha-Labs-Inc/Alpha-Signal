import json
from typing import Dict

from pydantic import BaseModel


def load_config(file_path: str, model):
    with open(file_path, "r") as file:
        data = json.load(file)
    return model(**data)


def update_config(file_path: str, updated_data: Dict):
    # Load the current data from the JSON file
    with open(file_path, "r") as file:
        data = json.load(file)

    # Update the existing data with the new data
    data.update(updated_data)

    # Save the updated data back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
