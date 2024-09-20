from __future__ import annotations

import arcade
import arcade.gui
import arcade.gl as gl
import pyglet
from arcade.types import Color
from arcade.experimental import Shadertoy

from shadow_of_doubt.gui.views import pause_menu
from shadow_of_doubt.assets import RoguelikeInterior
from shadow_of_doubt.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    CHARACTER_SCALING,
    TILE_SCALING,
    PLAYER_MOVEMENT_SPEED,
    GRAVITY,
    PLAYER_JUMP_SPEED,
    MAX_LIGHTS,
)


class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.window.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.AMAZON)
        arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.NEAREST, gl.NEAREST
        self.spritesheet = RoguelikeInterior()

        self.scene = self.create_scene()
        self.player_sprite = arcade.Sprite(
            self.spritesheet.get_sprite("potted-plant-1"),
            scale=CHARACTER_SCALING,
        )
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()

        self.left_key_down: bool = False
        self.right_key_down: bool = False

        self.reset()
        self.set_window_position()

        self.light_sprites = set()
        self.light_toggle_map: dict[str, str] = {
            "white-candelabra": "white-candelabra-lit",
            "white-candelabra-lit": "white-candelabra",
            "yellow-candelabra": "yellow-candelabra-lit",
            "yellow-candelabra-lit": "yellow-candelabra",
        }

        # Set up the shader
        self.setup_shader()

        # Setup lights
        self.setup_lights()

        # Set up the ui
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.pause_menu = pause_menu.PauseMenu(self, self.camera_sprites)

    def setup_shader(self) -> None:
        window_size = self.window.get_size()
        self.shadertoy = Shadertoy.create_from_file(window_size, "assets/shadow_shader.glsl")

        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel2 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.shadertoy.channel_0 = self.channel0.color_attachments[0]
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]
        self.shadertoy.channel_2 = self.channel2.color_attachments[0]

    def setup_lights(self) -> None:
        for layer_name in (
            "UnlitLights",
            "LitLights",
        ):
            to_remove = []
            for light in self.scene[layer_name]:
                if "name" not in light.properties:
                    continue
                texture_name = light.properties["name"]
                sprite = arcade.Sprite(
                    self.spritesheet.get_sprite(texture_name), scale=TILE_SCALING
                )
                sprite.position = light.position
                sprite.properties["texture_name"] = texture_name
                self.light_sprites.add(sprite)
                self.scene.add_sprite(layer_name, sprite)
                to_remove.append(light)

            for light in to_remove:
                light.remove_from_sprite_lists()

    def toggle_light(self, light: arcade.Sprite) -> None:
        texture_name = light.properties["texture_name"]
        new_texture_name = self.light_toggle_map[texture_name]
        light.texture = self.spritesheet.get_sprite(new_texture_name)
        light.properties["texture_name"] = new_texture_name
        if light in self.scene["UnlitLights"]:
            self.scene["UnlitLights"].remove(light)
            self.scene["LitLights"].append(light)
        else:
            self.scene["LitLights"].remove(light)
            self.scene["UnlitLights"].append(light)

    def set_window_position(self) -> None:
        display = pyglet.display.get_display()
        screens = display.get_screens()
        if len(screens) > 1:
            self.window.set_location(screens[1].x + 100, screens[1].y + 100)
        else:
            self.window.set_location(screens[0].x, screens[0].y)

    def create_scene(self) -> arcade.Scene:
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "UnlitLights": {
                "use_spatial_hash": True,
            },
            "LitLights": {
                "use_spatial_hash": True,
            },
        }
        tile_map = arcade.load_tilemap(
            "assets/level-1-map.tmx",
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        if tile_map.background_color:
            self.background_color = Color.from_iterable(tile_map.background_color)

        return arcade.Scene.from_tilemap(tile_map)

    def reset(self) -> None:
        self.scene = self.create_scene()
        self.player_sprite.position = (128, 128)
        self.scene.add_sprite_list("Player")
        self.scene["Player"].append(self.player_sprite)

    def on_draw(self) -> None:
        self.clear()

        # Draw platforms and the player to channel0
        self.channel0.use()
        self.channel0.clear()
        self.camera_sprites.use()
        self.scene["Player"].draw()
        self.scene["Platforms"].draw()

        # Draw everything else to channel1
        self.channel1.use()
        self.channel1.clear()
        self.camera_sprites.use()
        self.scene.draw()

        # Draw the player to channel2
        self.channel2.use()
        self.channel2.clear()
        self.camera_sprites.use()
        self.scene["Player"].draw()

        lights = []
        for light in self.scene["LitLights"]:
            left, bottom = self.camera_sprites.bottom_left
            lights.append((light.center_x - left, light.center_y - bottom))

        self.window.use()

        # Pad the lights list with (0, 0) to match MAX_LIGHTS from the shader
        lights = lights[:MAX_LIGHTS]
        while len(lights) < MAX_LIGHTS:
            lights.append((0, 0))

        self.shadertoy.program["lightPositions"] = [coord for light in lights for coord in light]
        self.shadertoy.program["lightSize"] = 500

        # Render the shader
        self.shadertoy.render()

        # set up the ui
        if self.pause_menu.paused:
            self.pause_menu.draw()

        self.manager.draw()

    def draw_title(self) -> None:
        text = arcade.Text(
            SCREEN_TITLE,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
        )
        text.draw()

    def update_player_speed(self) -> None:
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key: int, _: int) -> None:
        if key == arcade.key.ESCAPE:
            self.pause_menu.toggle_pause()
        elif not self.pause_menu.paused:
            if key == arcade.key.UP or key == arcade.key.W:
                if self.physics_engine.can_jump():
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left_key_down = True
                self.update_player_speed()
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_key_down = True
                self.update_player_speed()
            elif key == arcade.key.E:
                lights_hit_list = arcade.check_for_collision_with_list(
                    self.player_sprite, self.scene["UnlitLights"]
                ) + arcade.check_for_collision_with_list(
                    self.player_sprite, self.scene["LitLights"]
                )
                for light in lights_hit_list:
                    self.toggle_light(light)

    def on_key_release(self, key: int, _: int) -> None:
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()

    def center_camera_to_player(self) -> None:
        screen_center_x = self.player_sprite.center_x
        screen_center_y = self.player_sprite.center_y

        if screen_center_x - self.window.width / 2 < 0:
            screen_center_x = self.window.width / 2
        if screen_center_y - self.window.height / 2 < 0:
            screen_center_y = self.window.height / 2

        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position,
            player_centered,
            0.1,
        )

    def on_update(self, _: float) -> None:
        if not self.pause_menu.paused:
            self.physics_engine.update()
            self.center_camera_to_player()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.camera_sprites.match_screen(and_projection=True)
        self.camera_gui.match_screen(and_projection=True)
        self.shadertoy.resize((width, height))
        self.manager.on_resize(width, height)
