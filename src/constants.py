from pathlib import Path


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = ""
# Path to the game's root directory
_path = Path("src")
try:
    ROOT_DIR = _path.resolve(strict=True)
except FileNotFoundError as e:
    raise RuntimeError(
        "Root dir not found. Perhaps try to run the project from root and not inside src."
    ) from e

# Path to the game's assets directory
ASSETS_DIR = ROOT_DIR / "assets"
