import arcade
import arcade.gl as gl
import arcade.gui
import pyglet
from arcade.experimental import Shadertoy
from arcade.types import Color

from assets import RoguelikeInterior
from components.sprites.player import Player
from constants import (
    CHARACTER_POSITION,
    CHARACTER_SCALING,
    DEFAULT_DAMPING,
    GRAVITY,
    MAX_LIGHTS,
    PLAYER_FRICTION,
    PLAYER_MASS,
    PLAYER_MAX_HORIZONTAL_SPEED,
    PLAYER_MAX_VERTICAL_SPEED,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    TILE_SCALING,
    WALL_FRICTION,
)


class Window(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()
        arcade.set_background_color(arcade.color.AMAZON)
        arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.NEAREST, gl.NEAREST
        self.spritesheet = RoguelikeInterior()

        self.scene = self.create_scene()
        self.player_sprite = Player(
            scene=self.scene, position=CHARACTER_POSITION, scale=CHARACTER_SCALING
        )
        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=DEFAULT_DAMPING,
            gravity=(0, -GRAVITY),
        )
        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
        )
        self.physics_engine.add_sprite_list(
            self.scene["Platforms"],
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )
        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()

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

    def setup_shader(self) -> None:
        window_size = self.get_size()
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
            self.set_location(screens[1].x + 100, screens[1].y + 100)
        else:
            self.set_location(screens[0].x, screens[0].y)

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
            "Gold": {"use_spatial_hash": True},
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
        self.player_sprite.reset(self.scene)
        self.scene.add_sprite_list("Player")
        self.scene["Player"].append(self.player_sprite)

    def on_draw(self) -> None:
        self.clear()

        # Draw platforms, the player, and the gold to channel0
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
        self.player_sprite.score.draw()

        # Draw the player to channel2
        self.channel2.use()
        self.channel2.clear()
        self.camera_sprites.use()
        self.scene["Player"].draw()

        lights = []
        for light in self.scene["LitLights"]:
            left, bottom = self.camera_sprites.bottom_left
            lights.append((light.center_x - left, light.center_y - bottom))

        self.use()

        # Pad the lights list with (0, 0) to match MAX_LIGHTS from the shader
        lights = lights[:MAX_LIGHTS]
        while len(lights) < MAX_LIGHTS:
            lights.append((0, 0))

        self.shadertoy.program["lightPositions"] = [coord for light in lights for coord in light]
        self.shadertoy.program["lightSize"] = 500

        # Render the shader
        self.shadertoy.render()

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

    def on_key_press(self, key: int, _: int) -> None:
        self.player_sprite.on_key_press(key, _)
        if key == arcade.key.E:
            lights_hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, self.scene["UnlitLights"]
            ) + arcade.check_for_collision_with_list(self.player_sprite, self.scene["LitLights"])
            for light in lights_hit_list:
                self.toggle_light(light)

    def on_key_release(self, key: int, _: int) -> None:
        self.player_sprite.on_key_release(key, _)

    def center_camera_to_player(self) -> None:
        screen_center_x = self.player_sprite.center_x
        screen_center_y = self.player_sprite.center_y

        if screen_center_x - self.width / 2 < 0:
            screen_center_x = self.width / 2
        if screen_center_y - self.height / 2 < 0:
            screen_center_y = self.height / 2

        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position,
            player_centered,
            0.1,
        )

    def on_update(self, delta_time: float) -> None:
        self.scene.update(delta_time)
        self.scene.update_animation(delta_time)
        self.physics_engine.step()
        self.center_camera_to_player()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.camera_sprites.match_screen(and_projection=True)
        self.camera_gui.match_screen(and_projection=True)
        self.shadertoy.resize((width, height))
