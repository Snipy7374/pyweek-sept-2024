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
        self.camera_sprites = camera_sprites

        self._create_buttons()

    def toggle_pause(self) -> None:
        self.view.window.set_mouse_visible(True)
        self.paused = not self.paused
        if self.paused:
            self.view.manager.add(self.anchor_layout)
        else:
            self.view.manager.remove(self.anchor_layout)

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
        self.anchor_layout = arcade.gui.UIAnchorLayout()
        menu_texture = arcade.load_texture(constants.ASSETS_DIR / "menu_texture.png")
        menu_texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, texture=menu_texture)
        background_pause_menu = arcade.gui.UIImage(
            texture=menu_texture,
            width=480,
            height=560,
        )
        self.anchor_layout.add(
            background_pause_menu,
            anchor_x="center",
            anchor_y="center",
        )

        button_container = arcade.gui.UIBoxLayout(space_between=20)

        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        for text, action in self.button_info:
            button = arcade.gui.UITextureButton(
                text=text,
                width=button_width,
                height=button_height,
                texture=texture,
                texture_hovered=texture,
                texture_pressed=texture,
            )
            button.on_click = action  # type: ignore
            button_container.add(button)
        self.anchor_layout.add(
            button_container,
            anchor_x="center",
            anchor_y="center",
        )

    def draw(self) -> None:
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(
                left=self.camera_sprites.position[0] - constants.SCREEN_WIDTH // 2,
                right=self.camera_sprites.position[0] + constants.SCREEN_WIDTH // 2,
                top=self.camera_sprites.position[1] + constants.SCREEN_HEIGHT // 2,
                bottom=self.camera_sprites.position[1] - constants.SCREEN_HEIGHT // 2,
                color=(0, 0, 0, 200),
            )
