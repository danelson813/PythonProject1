import tomllib


class LocatorConfig:
    """Recursively converts a dictionary into an object for dot notation access."""

    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                # If the value is a dictionary, convert it recursively
                setattr(self, key, LocatorConfig(value))
            else:
                # Otherwise, just set the attribute
                setattr(self, key, value)


def load_locators(file_path="locators.toml"):
    # Load the TOML file
    with open(file_path, "rb") as file:
        raw_dict = tomllib.load(file)

    # Wrap the dictionary in our new helper class
    return LocatorConfig(raw_dict)
