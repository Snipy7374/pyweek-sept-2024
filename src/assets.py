import arcade
from constants import ASSETS_DIR


class RoguelikeInterior:
    def __init__(self):
        self.path = ASSETS_DIR / "roguelike-interior.png"
        self.spritesheet = arcade.load_spritesheet(self.path)
        self.tile_size = 16
        self.spacing = 1
        self.sprites = {
            "potted-plant-1": self.get_tile(16, 0),
            "potted-plant-2": self.get_tile(17, 0),
            "white-candelabra": self.get_tile(19, 0),
            "white-candelabra-lit": self.get_tile(19, 1),
            "yellow-candelabra": self.get_tile(20, 0),
            "yellow-candelabra-lit": self.get_tile(20, 1),
        }

    def get_sprite(self, name):
        return self.sprites[name]

    def get_tile(self, x, y):
        return self.spritesheet.get_texture(
            x * self.tile_size + x * self.spacing,
            y * self.tile_size + y * self.spacing,
            self.tile_size,
            self.tile_size,
            None,
            "upper_left",
        )
