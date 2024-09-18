import arcade
import numpy as np
from arcade import gl


class ShadowSprite(arcade.Sprite):
    def __init__(self, player_sprite, light_sprite, ground_y):
        super().__init__()
        self.width = player_sprite.width
        self.height = player_sprite.height
        self.player_sprite = player_sprite
        self.light_sprite = light_sprite
        self.ground_y = ground_y

        self.ctx = arcade.get_window().ctx

        self.program = self.create_shader_program()

        # Create a render target (framebuffer) for the shadow
        self.shadow_texture = self.ctx.texture((int(self.width), int(self.height)), components=4)

        # Create GL texture from the sprite's texture
        image = self.player_sprite.texture.image
        self.gl_texture = self.ctx.texture(
            size=image.size,
            components=4,
            data=image.convert("RGBA").tobytes(),
        )

        # Create geometry (quad)
        vertices = np.array(
            [
                # x, y, u, v
                -self.width / 2,
                -self.height / 2,
                0.0,
                0.0,
                self.width / 2,
                -self.height / 2,
                1.0,
                0.0,
                self.width / 2,
                self.height / 2,
                1.0,
                1.0,
                -self.width / 2,
                self.height / 2,
                0.0,
                1.0,
            ],
            dtype="f4",
        )

        indices = np.array([0, 1, 2, 2, 3, 0], dtype="i4")

        vertex_buffer = self.ctx.buffer(data=vertices.tobytes())
        index_buffer = self.ctx.buffer(data=indices.tobytes())

        self.geometry = self.ctx.geometry(
            [gl.BufferDescription(vertex_buffer, "2f 2f", ["in_vert", "in_uv"])], index_buffer
        )

    def create_shader_program(self):
        return self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;
            uniform mat3 transform;
            void main() {
                vec3 pos = transform * vec3(in_vert, 1.0);
                gl_Position = vec4(pos.xy, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D texture0;
            void main() {
                vec4 color = texture(texture0, v_uv);
                f_color = vec4(0.0, 0.0, 0.0, color.a * 0.5);
            }
            """,
        )

    def update(self, delta_time: float = 1 / 60):
        self.position = self.player_sprite.position
        self.angle = self.player_sprite.angle
        self.scale = self.player_sprite.scale

        self.update_shadow_transform()

    def update_shadow_transform(self):
        # Calculate shadow transformation based on light and player positions
        px, py = self.player_sprite.position
        lx, _ = self.light_sprite.position
        dy = py - self.ground_y
        if abs(dy) < 0.001:
            dy = 0.001  # Avoid division by zero
        kx = (lx - px) / dy

        # Handle scale as either a single value or a tuple/list
        if isinstance(self.scale, (int, float)):
            scale_x = scale_y = float(self.scale)
        else:
            scale_x, scale_y = map(float, self.scale[:2])

        # Create transformation matrices using numpy
        scale_matrix = np.array([[scale_x, 0, 0], [0, scale_y, 0], [0, 0, 1]], dtype=np.float32)

        rotation_matrix = np.array(
            [
                [np.cos(np.radians(self.angle)), -np.sin(np.radians(self.angle)), 0],
                [np.sin(np.radians(self.angle)), np.cos(np.radians(self.angle)), 0],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

        shear_matrix = np.array([[1, kx, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)

        translation_matrix = np.array(
            [[1, 0, self.center_x], [0, 1, self.center_y], [0, 0, 1]], dtype=np.float32
        )

        self.transform = translation_matrix @ shear_matrix @ rotation_matrix @ scale_matrix

    def draw_shadow(self):
        self.ctx.enable(self.ctx.BLEND)
        self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        self.program["transform"] = self.transform.flatten()
        self.program["texture0"] = 0

        self.gl_texture.use(0)

        self.geometry.render(self.program)
