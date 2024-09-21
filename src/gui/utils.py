import json
from typing import Any

import constants


def load_settings() -> dict[str, Any]:
    with open(constants.SETTINGS_DIR / "saved_settings.json") as f:
        data = json.load(f)
    return data
