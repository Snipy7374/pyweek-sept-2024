import arcade

import constants
from menus import MainMenuView


def main() -> None:
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
        resizable=True,
    )

    main_menu = MainMenuView()
    window.show_view(main_menu)
    main_menu.setup()
    window.run()


if __name__ == "__main__":
    main()
