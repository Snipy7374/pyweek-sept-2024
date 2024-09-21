import json
import arcade

import constants
from gui.views import MainMenuView
from gui.utils import load_settings


def ensure_settings_file() -> None:
    if not constants.SETTINGS_DIR.exists():
        constants.SETTINGS_DIR.mkdir(parents=True)

    path = constants.SETTINGS_DIR / "saved_settings.json"
    if not path.exists():
        with open(path, "w") as f:
            json.dump(constants.DEFAULT_SETTINGS, f, indent=2)


def main() -> None:
    ensure_settings_file()
    settings = load_settings()
    try:
        size = settings["window_size_dropdown"]
        if size:
            width, height = map(int, size.split("x"))
        else:
            width, height = arcade.get_display_size()
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

    main_menu = MainMenuView(
        settings.get("current_level", 1),
        settings.get("shader_toggle", False),
    )
    window.show_view(main_menu)
    main_menu.setup()
    window.run()


if __name__ == "__main__":
    main()
