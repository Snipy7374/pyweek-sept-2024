from __future__ import annotations
import typing

import arcade
import arcade.gui

from shadow_of_doubt.gui.views import main_menu
from shadow_of_doubt import constants

if typing.TYPE_CHECKING:
    from shadow_of_doubt.window import GameView


class PauseMenu:
    def __init__(self, view: GameView, camera_sprites) -> None:
        self.view = view
        self.paused = False
        self.buttons = []
        self.camera_sprites = camera_sprites

        self._create_buttons()

    def toggle_pause(self) -> None:
        self.view.window.set_mouse_visible(True)
        self.paused = not self.paused
        if self.paused:
            for button in self.buttons:
                self.view.manager.add(button)
        else:
            for button in self.buttons:
                self.view.manager.remove(button)

    def resume_game(self, _) -> None:
        self.toggle_pause()

    def go_to_main_menu(self, _) -> None:
        view = main_menu.MainMenuView()
        view.setup()
        self.view.window.show_view(view)

    def exit_game(self, _) -> None:
        arcade.exit()

    def _create_buttons(self) -> None:
        button_width = 320
        button_height = 100
        self.button_info = [
            ("Resume", self.resume_game),
            ("Main Menu", self.go_to_main_menu),
            ("Exit", self.exit_game),
        ]
        start_y = (
            (self.view.window.height // 2)
            + int((button_height // 2) * len(self.button_info))
            - button_height
        )
        start_x = (self.view.window.width // 2) - (button_width // 2)
        button_spacing = 20

        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        for text, action in self.button_info:
            button = arcade.gui.UITextureButton(
                text=text,
                width=button_width,
                height=button_height,
                x=start_x,
                y=start_y,
                texture=texture,
                texture_hovered=texture,
                texture_pressed=texture,
            )
            button.on_click = typing.cast(
                typing.Callable[[arcade.gui.UITextureButton], None], action
            )
            self.buttons.append(button)
            start_y -= button_height + button_spacing

    def draw(self) -> None:
        if self.paused:
            menu_texture = arcade.load_texture(constants.ASSETS_DIR / "menu_texture.png")
            x = self.view.window.width // 2
            y = (self.view.window.height // 2) - 20
            arcade.draw_texture_rect(
                texture=menu_texture,
                rect=arcade.Rect.from_kwargs(
                    x=x,
                    y=y,
                    width=480,
                    height=560,
                ),
                pixelated=True,
                alpha=200,
            )
