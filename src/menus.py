import arcade
import arcade.gui
import arcade.gui.experimental

import constants
from window import GameView


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
            y=300,
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
        view = GameView()
        self.window.show_view(view)

    def options_callback(self, _: arcade.gui.UIFlatButton) -> None:
        view = SubMenu(
            "Options",
            "sus",
            "sus",
            ["sus"],
            "sus",
        )
        self.manager.add(view)

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
            width=400,
            height=400,
        )
        self.scroll_area.scroll_speed = 20
        self.manager.add(self.scroll_area)

    def setup(self) -> None:
        ...

    def on_hide_view(self) -> None:
        self.manager.disable()

    def on_show_view(self) -> None:
        self.manager.enable()

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()


class SubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    """Acts like a fake view/window."""

    def __init__(
        self,
        title: str,
        input_text: str,
        toggle_label: str,
        dropdown_options: list[str],
        slider_label: str,
    ):
        super().__init__(size_hint=(1, 1))

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=300, height=400, size_hint=None))
        frame.with_padding(all=20)
        frame.with_background(color=arcade.color.BLUE)

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        # The type of event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(height=30, color=arcade.color.BLUE)

        # Align toggle and label horizontally next to each other
        toggle_group = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        toggle_label = arcade.gui.UILabel(text=toggle_label)
        # Create dropdown with a specified default.
        dropdown = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options, height=20, width=250
        )

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)
        widget_layout.add(title_label)
        widget_layout.add(title_label_space)
        widget_layout.add(toggle_group)
        widget_layout.add(dropdown)

        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent.remove(self)
