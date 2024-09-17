import arcade
import arcade.gui
from pathlib import Path


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Shadow of Doubt"

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

CHARACTER_SCALING = 4
TILE_SCALING = 3

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

MAX_LIGHTS = 100

arcade.load_font(FONTS_DIR / "Fantasya-Bold.otf")
arcade.load_font(FONTS_DIR / "Fantasya.otf")
MAIN_MENU_BUTTONS_STYLE = arcade.gui.UIFlatButton.DEFAULT_STYLE
MAIN_MENU_BUTTONS_STYLE.update(
    {
        "normal": arcade.gui.UIFlatButton.UIStyle(
            font_name="Fantasya",
            font_size=32,
        ),
    }
)
MAIN_MENU_BUTTONS_STYLE["hover"].font_name = "Fantasya"
MAIN_MENU_BUTTONS_STYLE["hover"].font_size = 32
