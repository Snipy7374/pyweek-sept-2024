import arcade
import arcade.gui

from shadow_of_doubt.constants import FONTS_DIR


arcade.load_font(FONTS_DIR / "DungeonFont.ttf")
MAIN_MENU_BUTTONS_STYLE = arcade.gui.UITextureButton.DEFAULT_STYLE
MAIN_MENU_BUTTONS_STYLE.update(
    {
        "normal": arcade.gui.UITextureButton.UIStyle(
            font_name="DungeonFont",
            font_size=32,
        ),
    }
)
MAIN_MENU_BUTTONS_STYLE["hover"].font_name = "DungeonFont"
MAIN_MENU_BUTTONS_STYLE["hover"].font_size = 32
MAIN_MENU_BUTTONS_STYLE["press"].font_name = "DungeonFont"
MAIN_MENU_BUTTONS_STYLE["press"].font_size = 32
