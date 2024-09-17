import arcade
import arcade.gui
import arcade.gui.experimental

from shadow_of_doubt import constants, styles, __version__
from shadow_of_doubt.window import GameView


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
        self.box = arcade.gui.UIBoxLayout(
            x=50,
            y=int(self.window.center_y) - 220,
            space_between=25,
        )
        # background gif
        # button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        # texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        # self.manager.add(arcade.gui.UIImage(
        #    texture=texture,
        #    width=self.window.width,
        #    height=self.window.height
        # ))
        game_title = arcade.gui.UILabel(
            constants.SCREEN_TITLE,
            x=self.window.center_x - 310,
            y=self.window.height - 160,
            font_name="DungeonFont",
            font_size=72,
        )
        footer_label = arcade.gui.UILabel(
            constants.COPYRIGHT_AND_LICENSE_NOTICE,
            x=self.window.center_x - 310,
            y=50,
            bold=True,
            font_size=14,
        )
        version_label = arcade.gui.UILabel(
            "v" + __version__,
            x=15,
            y=50,
            bold=True,
            font_size=14,
        )
        self.manager.add(game_title, layer=1)
        self.manager.add(footer_label, layer=1)
        self.manager.add(version_label, layer=1)
        self.manager.add(self.box, layer=1)

    def setup(self) -> None:
        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        for i, label in enumerate(self.BUTTONS):
            i += 1
            button = arcade.gui.UITextureButton(
                x=100,
                y=100,
                text=label,
                width=350,
                height=100,
                style=styles.MAIN_MENU_BUTTONS_STYLE,
                texture=texture,
                texture_hovered=texture,
                texture_pressed=texture,
            )

            button.set_handler(
                "on_click", self.__getattribute__(label.lower().replace(" ", "_") + "_callback")
            )
            self.box.add(
                child=button,
            )

        self.box.prepare_layout()

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
        texture = arcade.load_texture(constants.ASSETS_DIR / "solid_black.png")
        background = arcade.gui.UIImage(
            texture=texture,
            width=self.window.width,
            height=self.window.height,
        )
        background.alpha = 100
        self.manager.add(
            background,
            layer=1,
        )
        view = SubMenu(
            self.manager,
            "Options",
            ["sus"],
            background,
        )
        self.manager.add(view, layer=2)

    def credits_callback(self, _: arcade.gui.UIFlatButton) -> None:
        print("Credits")

    def exit_callback(self, _: arcade.gui.UIFlatButton) -> None:
        self.window.close()


class SubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    def __init__(
        self,
        parent_manager: arcade.gui.UIManager,
        title: str,
        dropdown_options: list[str],
        backgound_child: arcade.gui.UIWidget,
    ):
        super().__init__(size_hint=(1, 1))
        self.parent_manager = parent_manager
        self.background_child = backgound_child

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=800, height=700, size_hint=None))
        frame.with_padding(all=20)
        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        frame.with_background(texture=texture)

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        # The type of event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(height=30)

        # Align toggle and label horizontally next to each other
        toggle_group = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        # Create dropdown with a specified default.
        dropdown = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options, height=20, width=250
        )

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)
        widget_layout.add(title_label_space)
        widget_layout.add(title_label_space)
        widget_layout.add(title_label)
        widget_layout.add(title_label_space)
        widget_layout.add(toggle_group)
        widget_layout.add(dropdown)

        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent_manager.remove(self)
        self.parent_manager.remove(self.background_child)
