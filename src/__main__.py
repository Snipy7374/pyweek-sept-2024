import arcade

from shadow_of_doubt import constants
from shadow_of_doubt.gui.views import MainMenuView


def main() -> None:
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
        center_window=True,
    )

    main_menu = MainMenuView()
    window.show_view(main_menu)
    main_menu.setup()
    window.run()


if __name__ == "__main__":
    main()
