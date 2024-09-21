import enum
import math
from PIL import Image

import arcade

from constants import ASSETS_DIR


class BarColors(str, enum.Enum):
    BLUE = "blue"
    BROWN = "brown"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"


class BarIcons(str, enum.Enum):
    HEALTH = "health"
    MAGIC = "magic"
    POWER = "power"
    SHIELD = "shield"
    STAMINA = "stamina"
    TIMER = "timer"
    XP = "xp"


class Bar:
    _repeats = 6

    def __init__(
        self,
        color: BarColors,
        icon: BarIcons,
        current_value: int,
        max_value: int,
        scale: float = 1.0,
    ) -> None:
        self.color = color.value
        self.icon = icon.value
        self.current_value = current_value
        self.max_value = max_value
        self.scale = scale
        self.textures = []
        self.load_assets()

    def load_assets(self) -> None:
        self.icon_image = arcade.load_image(ASSETS_DIR / "bars" / "icons" / f"{self.icon}.png")
        self.bar_images = {
            "icon_holder": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_icon_holder_{self.color}.png"
            ),
            "left_edge": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_bar_holder_left_edge_{self.color}.png"
            ),
            "center": arcade.load_image(
                ASSETS_DIR
                / "bars"
                / self.color
                / f"meter_bar_holder_center-repeating_{self.color}.png"
            ),
            "right_edge": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_bar_holder_right_edge_{self.color}.png"
            ),
            "text_background_left": arcade.load_image(
                ASSETS_DIR
                / "bars"
                / self.color
                / f"meter_text_background_left_edge_{self.color}.png"
            ),
            "text_background_center": arcade.load_image(
                ASSETS_DIR
                / "bars"
                / self.color
                / f"meter_text_background_center_repeating_{self.color}.png"
            ),
            "text_background_right": arcade.load_image(
                ASSETS_DIR
                / "bars"
                / self.color
                / f"meter_text_background_right_edge_{self.color}.png"
            ),
        }
        self.fill_images = {
            "left_edge": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_bar_left_edge_{self.color}.png"
            ),
            "center": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_bar_center-repeating_{self.color}.png"
            ),
            "right_edge": arcade.load_image(
                ASSETS_DIR / "bars" / self.color / f"meter_bar_right_edge_{self.color}.png"
            ),
        }

        bar_width = (
            self.bar_images["left_edge"].width
            + self.bar_images["right_edge"].width
            + self._repeats * self.bar_images["center"].width
        )
        icon_holder_width = self.bar_images["icon_holder"].width
        icon_holder_height = self.bar_images["icon_holder"].height
        bar_image = Image.new(
            "RGBA", (bar_width + icon_holder_width, icon_holder_height), color=(0, 0, 0, 0)
        )
        by = icon_holder_height // 8
        bx = icon_holder_width // 3
        bar_image.paste(self.bar_images["left_edge"], (icon_holder_width - bx, by))
        for i in range(self._repeats):
            bar_image.paste(
                self.bar_images["center"],
                (
                    icon_holder_width
                    + self.bar_images["left_edge"].width
                    - bx
                    + i * self.bar_images["center"].width,
                    by,
                ),
            )
        bar_image.paste(
            self.bar_images["right_edge"],
            (icon_holder_width + bar_width - bx - self.bar_images["right_edge"].width, by),
        )
        self.bar_image = bar_image

        icon_image = Image.new("RGBA", (icon_holder_width, icon_holder_height), color=(0, 0, 0, 0))
        icon_image.paste(self.bar_images["icon_holder"], (0, 0))
        x1, y1, w1, h1 = 0, 0, icon_holder_width, icon_holder_height
        w2, h2 = self.icon_image.width, self.icon_image.height
        x2, y2 = x1 + ((w1 - w2) // 2), y1 + ((h1 - h2) // 2)
        icon_image.paste(self.icon_image, (x2, y2), self.icon_image)
        self.icon_image = icon_image

        self._bar_states = [self.construct_bar_image(i) for i in range(self.max_value + 1)]
        for bar_state in self._bar_states:
            self.textures.append(arcade.Texture(bar_state))

    def construct_bar_image(self, state: int) -> Image.Image:
        bar_width = (
            self.bar_images["left_edge"].width
            + self.bar_images["right_edge"].width
            + self._repeats * self.bar_images["center"].width
        )
        icon_holder_width = self.bar_images["icon_holder"].width
        icon_holder_height = self.bar_images["icon_holder"].height
        bx = icon_holder_width // 3
        by = icon_holder_height // 8
        bar_image = self.bar_image.copy()
        fill_width = math.ceil((state / self.max_value) * bar_width)
        fill_image = Image.new(
            "RGBA", (fill_width, self.fill_images["left_edge"].height), color=(0, 0, 0, 0)
        )
        fill_image.paste(self.fill_images["left_edge"], (0, 0))
        center_width = (
            fill_width - self.fill_images["left_edge"].width - self.fill_images["right_edge"].width
        )
        for i in range(math.ceil(center_width / self.fill_images["center"].width)):
            fill_image.paste(
                self.fill_images["center"],
                (self.fill_images["left_edge"].width + i * self.fill_images["center"].width, 0),
            )
        fill_image.paste(
            self.fill_images["right_edge"], (fill_width - self.fill_images["right_edge"].width, 0)
        )
        bar_image.paste(fill_image, (icon_holder_width - bx + 10, by), fill_image)
        bar_image.paste(self.icon_image, (0, 0), self.icon_image)
        return bar_image

    @property
    def texture(self) -> arcade.Texture:
        return self.textures[self.current_value]

    @property
    def value(self) -> int:
        return self.current_value

    @value.setter
    def value(self, value: int) -> None:
        self.current_value = value
