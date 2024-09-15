import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        text = arcade.Text(
            "Welcome to Arcade",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
        )
        text.draw()
