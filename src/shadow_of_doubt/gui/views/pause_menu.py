from __future__ import annotations
import typing

import arcade
import arcade.gui

from shadow_of_doubt.gui.views import options_menu, main_menu
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

    def show_options(self, _) -> None:
        temp_layout = arcade.gui.UIAnchorLayout()
        view = options_menu.OptionsMenu(main_view=self.view, temp_manager=temp_layout)
        view.setup_from_dict()
        temp_layout.add(view, anchor_x="center", anchor_y="center")
        self.view.manager.add(temp_layout, layer=1)

    def go_to_main_menu(self, _) -> None:
        view = main_menu.MainMenuView()
        view.setup()
        self.view.window.show_view(view)

    def exit_game(self, _) -> None:
        arcade.exit()

    def _create_buttons(self) -> None:
        button_width = 200
        button_height = 50
        start_y = constants.SCREEN_HEIGHT // 2 + 100
        button_spacing = 20

        button_info = [
            ("Resume", self.resume_game),
            ("Options", self.show_options),
            ("Main Menu", self.go_to_main_menu),
            ("Exit", self.exit_game),
        ]

        for i, (text, action) in enumerate(button_info):
            button = arcade.gui.UIFlatButton(
                text=text,
                width=button_width,
                height=button_height,
                x=constants.SCREEN_WIDTH // 2 - button_width // 2,
                y=start_y - i * (button_spacing + button_height),
            )
            button.on_click = action
            self.buttons.append(button)

    def draw(self) -> None:
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(
                left=self.camera_sprites.position[0] - constants.SCREEN_WIDTH // 2,
                right=self.camera_sprites.position[0] + constants.SCREEN_WIDTH // 2,
                top=self.camera_sprites.position[1] + constants.SCREEN_HEIGHT // 2,
                bottom=self.camera_sprites.position[1] - constants.SCREEN_HEIGHT // 2,
                color=(0, 0, 0, 200),
            )
            for button in self.buttons:
                self.view.manager.add(button)
