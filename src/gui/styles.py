import arcade
import arcade.gui

from constants import FONTS_DIR

arcade.load_font(FONTS_DIR / "Alagard.ttf")
MAIN_MENU_BUTTONS_STYLE = arcade.gui.UITextureButton.DEFAULT_STYLE
MAIN_MENU_BUTTONS_STYLE.update(
    {
        "normal": arcade.gui.UITextureButton.UIStyle(
            font_name="Alagard",
            font_size=32,
        ),
    }
)
MAIN_MENU_BUTTONS_STYLE["hover"].font_name = "Alagard"
MAIN_MENU_BUTTONS_STYLE["hover"].font_size = 32
MAIN_MENU_BUTTONS_STYLE["press"].font_name = "Alagard"
MAIN_MENU_BUTTONS_STYLE["press"].font_size = 32
MAIN_MENU_BUTTONS_STYLE["disabled"].font_name = "Alagard"
MAIN_MENU_BUTTONS_STYLE["disabled"].font_size = 32
