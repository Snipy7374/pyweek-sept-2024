import webbrowser
import typing as t

import arcade
import arcade.gui
from arcade.future.light import LightLayer, Light

import window
import constants
from gui import styles
from gui.views.options_menu import OptionsMenu


__version__ = "0.1.0"


class MainMenuView(arcade.View):
    BUTTONS: tuple[str, ...] = (
        "Start Game",
        "Options",
        "Credits",
        "Exit",
    )

    def __init__(
        self,
        current_level: int,
        shader_enabled: bool,
    ) -> None:
        super().__init__()
        self.shader_enabled = shader_enabled
        self.current_level = current_level
        self.manager = arcade.gui.UIManager()
        self.ui_layout = arcade.gui.UIAnchorLayout()
        self.box = arcade.gui.UIBoxLayout(
            x=50,
            y=int(self.window.center_y) - 220,
            space_between=20,
        )

        # background gif
        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        self.manager.add(
            arcade.gui.UIImage(
                texture=texture,
                width=self.window.width,
                height=self.window.height,
                size_hint=(1, 1),
            )
        )

        game_title = arcade.gui.UILabel(
            constants.SCREEN_TITLE,
            x=self.window.center_x - 310,
            y=self.window.height - 160,
            font_name="Alagard",
            font_size=72,
        )
        footer_label = arcade.gui.UILabel(
            constants.COPYRIGHT_AND_LICENSE_NOTICE,
            x=self.window.center_x - 310,
            y=50,
            bold=True,
            font_size=12,
            size_hint=(0, 0),
            size_hint_max=(1000, 25),
        )
        version_label = arcade.gui.UILabel(
            "v" + __version__,
            x=15,
            y=50,
            bold=True,
            font_size=14,
        )
        self.ui_layout.add(
            game_title,
            anchor_x="center",
            anchor_y="center",
            align_y=275,
        )
        self.ui_layout.add(
            footer_label,
            anchor_x="center",
            anchor_y="bottom",
            align_y=10,
        )
        self.ui_layout.add(
            version_label,
            anchor_x="left",
            anchor_y="bottom",
            align_x=20,
            align_y=10,
        )
        self.ui_layout.add(
            self.box,
            anchor_x="left",
            anchor_y="center",
            align_x=40,
        )
        self.manager.add(self.ui_layout, layer=0)

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
                style=t.cast(dict[str, arcade.gui.UIStyleBase], styles.MAIN_MENU_BUTTONS_STYLE),
                texture=texture,
                texture_hovered=texture,
                texture_pressed=texture,
                size_hint=(1, 1),
                size_hint_min=(320, 75),
                size_hint_max=(350, 100),
            )

            button.set_handler(
                "on_click", self.__getattribute__(label.lower().replace(" ", "_") + "_callback")
            )
            self.box.add(
                child=button,
            )

        self.box.prepare_layout()
        self.light_layer = LightLayer(self.window.width, self.window.height)
        self.light_layer.set_background_color(arcade.csscolor.BLACK)

        # create a large white light in the center of the screen
        self.light = Light(
            self.window.center_x,
            self.window.center_y,
            500,
            arcade.csscolor.LIGHT_YELLOW,
            "soft",
        )
        self.light_layer.add(self.light)

        # add the light pointing to the menu
        light = Light(
            240,
            self.window.height // 2,
            600,
            arcade.csscolor.WHITE,
            "soft",
        )
        self.light_layer.add(light)

        # light to see the title
        light = Light(
            self.window.center_x,
            self.window.height - 200,
            400,
            arcade.csscolor.MISTY_ROSE,
            "soft",
        )
        self.light_layer.add(light)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self.light.position = x, y

    def on_hide_view(self) -> None:
        self.manager.disable()

    def on_show_view(self) -> None:
        self.manager.enable()

    def on_draw(self) -> None:
        self.clear()
        with self.light_layer:
            self.manager.draw()
        self.light_layer.draw(ambient_color=(10, 10, 10))

    def start_game_callback(self, _: arcade.gui.UIFlatButton) -> None:
        view = window.GameView(
            current_level=self.current_level,
            shader_enabled=self.shader_enabled,
        )
        view.current_level = self.current_level
        self.window.show_view(view)

    def options_callback(self, _: arcade.gui.UIFlatButton) -> None:
        texture = arcade.load_texture(constants.ASSETS_DIR / "solid_black.png")
        background = arcade.gui.UIImage(
            texture=texture,
            width=self.window.width,
            height=self.window.height,
            size_hint=(1, 1),
        )
        background.alpha = 150
        self.manager.add(
            background,
            layer=1,
        )

        for btn in self.box:
            btn.disabled = True  # type: ignore

        temp_layout = arcade.gui.UIAnchorLayout()
        view = OptionsMenu(
            main_view=self,
            parent_manager=self.manager,
            temp_manager=temp_layout,
            backgound_child=background,
        )
        view.setup_from_dict()
        temp_layout.add(view, anchor_x="center", anchor_y="center")
        self.manager.add(temp_layout, layer=1)

    def credits_callback(self, _: arcade.gui.UIFlatButton) -> None:
        webbrowser.open(constants.CREDITS_SECTION_ULR)

    def exit_callback(self, _: arcade.gui.UIFlatButton) -> None:
        self.window.close()
