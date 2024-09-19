from pathlib import Path


SCREEN_WIDTH = 1365
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Shadow of Doubt"
COPYRIGHT_AND_LICENSE_NOTICE = "Copyright © 2024-present, see Credits for more info - Licensed under the MIT license."

# Path to the game's root directory
try:
    ROOT_DIR = Path("src").resolve(strict=True)
except FileNotFoundError as e:
    raise RuntimeError(
        "Root dir not found. Perhaps try to run the project from root and not inside src."
    ) from e

# Path to the game's assets directory
# we don't need to be strict here as ROOT
# if the user is in the wrong dir they will already get
# the error from above
ASSETS_DIR = Path("assets").resolve()
FONTS_DIR = ASSETS_DIR / "fonts"
SAVES_DIR = Path("saves").resolve()
SETTINGS_DIR = SAVES_DIR / "settings"

CHARACTER_SCALING = 4
TILE_SCALING = 3

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

MAX_LIGHTS = 100
