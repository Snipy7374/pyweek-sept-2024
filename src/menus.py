import arcade
import arcade.gui
import arcade.gui.experimental

import constants


class MainMenuView(arcade.View):
    BUTTONS: tuple[str, ...] = (
        "Start Game",
        "Options",
        "Credits",
        "Exit",
    )

    def __init__(self) -> None:
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.grid_box = arcade.gui.UIGridLayout(
            x=570,
            y=350,
            column_count=2,
            row_count=2,
            horizontal_spacing=50,
            vertical_spacing=50,
        )
        self.manager.add(self.grid_box)

    def setup(self) -> None:
        row: int = 0
        column: int = 0
        for i, label in enumerate(self.BUTTONS):
            i += 1
            button = arcade.gui.UIFlatButton(
                x=100,
                y=100,
                text=label,
                width=400,
                height=200,
                style=constants.MAIN_MENU_BUTTONS_STYLE,
            )

            button.set_handler(
                "on_click", self.__getattribute__(label.lower().replace(" ", "_") + "_callback")
            )

            self.grid_box.add(
                child=button,
                row=row,
                column=column,
            )
            row = i // 2
            column = i % 2

        self.grid_box.prepare_layout()

    def on_hide_view(self) -> None:
        self.manager.disable()

    def on_show_view(self) -> None:
        self.manager.enable()

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()

    def start_game_callback(self, _: arcade.gui.UIFlatButton) -> None:
        print("sus")

    def options_callback(self, _: arcade.gui.UIFlatButton) -> None:
        view = OptionsView()
        view.setup()
        self.window.show_view(view)

    def credits_callback(self, _: arcade.gui.UIFlatButton) -> None:
        print("Credits")

    def exit_callback(self, _: arcade.gui.UIFlatButton) -> None:
        self.window.close()


class OptionsView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.scroll_area = arcade.gui.experimental.UIScrollArea(
            x=570,
            y=350,
        )
        self.scroll_area.scroll_speed = 20
        self.manager.add(self.scroll_area)

    def setup(self) -> None:
        test_btn = arcade.gui.UIFlatButton(text="sus")
        test_btn1 = arcade.gui.UIFlatButton(text="sus1")
        self.scroll_area.add(test_btn)
        self.scroll_area.add(test_btn1)

    def on_hide_view(self) -> None:
        self.manager.disable()

    def on_show_view(self) -> None:
        self.manager.enable()

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()
