import arcade

from shadow_of_doubt import constants
from shadow_of_doubt.gui.views import MainMenuView
from shadow_of_doubt.gui.utils import load_settings


def main() -> None:
    settings = load_settings()
    try:
        width, height = map(int, settings["window_size_dropdown"].split("x"))
    except (KeyError, TypeError):
        width, height = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
    try:
        antialiasing_samples = int(settings["antialiasing_samples_dropdown"])
    except (KeyError, TypeError):
        antialiasing_samples = 4
    window = arcade.Window(
        width=width,
        height=height,
        title=constants.SCREEN_TITLE,
        center_window=True,
        vsync=settings.get("vsync_toggle") or True,
        antialiasing=settings.get("antialiasing_toggle") or False,
        samples=antialiasing_samples,
        fullscreen=settings.get("fullscreen_toggle") or False,
    )

    main_menu = MainMenuView()
    window.show_view(main_menu)
    main_menu.setup()
    window.run()


if __name__ == "__main__":
    main()
