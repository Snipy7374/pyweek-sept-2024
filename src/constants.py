from pathlib import Path


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Shadow of Doubt"
# Path to the game's root directory
_path = Path(__file__).parent.parent
try:
    ROOT_DIR = _path.resolve(strict=True)
except FileNotFoundError as e:
    raise RuntimeError(
        "Root dir not found. Perhaps try to run the project from root and not inside src."
    ) from e

# Path to the game's assets directory
ASSETS_DIR = ROOT_DIR / "assets"

CHARACTER_SCALING = 4
TILE_SCALING = 3

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

MAX_LIGHTS = 100
