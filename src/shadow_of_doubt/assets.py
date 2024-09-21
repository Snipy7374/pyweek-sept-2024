import enum
import pathlib

import arcade

from shadow_of_doubt.constants import ASSETS_DIR


class MainCharacterState(enum.IntEnum):
    IDLE = 0
    RUN = 1
    COMBO_ATTACK = 2
    DEATH = 3
    HURT = 4
    JUMP = 5
    EDGE_GRAB = 6
    EDGE_IDLE = 7
    WALL_SLIDE = 8
    CROUCH = 9
    DASH = 10
    DASH_ATTACK = 11
    SLIDE = 12
    LADDER_GRAB = 13


class MainCharacterAssets:
    # coin_collect_sound = arcade.load_sound(ASSETS_DIR / "sfx" / "coin.ogg")
    jump_sound = arcade.load_sound(ASSETS_DIR / "sfx" / "jump.wav")
    attack_sound = arcade.load_sound(ASSETS_DIR / "sfx" / "attack.wav")


class RoguelikeInterior:
    def __init__(self) -> None:
        self.path = ASSETS_DIR / "roguelike-interior.png"
        self.spritesheet = arcade.load_spritesheet(self.path)
        self.tile_size = 16
        self.spacing = 1
        self.sprites: dict[str, arcade.Texture] = {
            "potted-plant-1": self.get_tile(16, 0),
            "potted-plant-2": self.get_tile(17, 0),
            "white-candelabra": self.get_tile(19, 0),
            "white-candelabra-lit": self.get_tile(19, 1),
            "yellow-candelabra": self.get_tile(20, 0),
            "yellow-candelabra-lit": self.get_tile(20, 1),
        }

    def get_sprite(self, name: str) -> arcade.Texture:
        return self.sprites[name]

    def get_tile(self, x: int, y: int) -> arcade.Texture:
        return self.spritesheet.get_texture(
            x * self.tile_size + x * self.spacing,
            y * self.tile_size + y * self.spacing,
            self.tile_size,
            self.tile_size,
            origin="upper_left",
        )


class MainCharacter:
    character_width = 69
    character_height = 44
    animation_frames = {
        MainCharacterState.IDLE: 6,
        MainCharacterState.RUN: 8,
        MainCharacterState.COMBO_ATTACK: 12,
        MainCharacterState.DEATH: 11,
        MainCharacterState.HURT: 4,
        MainCharacterState.JUMP: 8,
        MainCharacterState.EDGE_GRAB: 5,
        MainCharacterState.EDGE_IDLE: 6,
        MainCharacterState.WALL_SLIDE: 3,
        MainCharacterState.CROUCH: 6,
        MainCharacterState.DASH: 7,
        MainCharacterState.DASH_ATTACK: 10,
        MainCharacterState.SLIDE: 5,
        MainCharacterState.LADDER_GRAB: 8,
    }
    current_state = MainCharacterState.IDLE
    current_frame = 0
    assets = MainCharacterAssets()

    def __init__(
        self,
        position: tuple[int, int],
        path: str | pathlib.Path = ASSETS_DIR / "main-character.png",
        scale: float = 1.0,
    ) -> None:
        self.path = path
        self.scale = scale
        self.position = position
        self.spritesheet = arcade.load_spritesheet(self.path)
        sheet_width, _ = self.spritesheet._image.size  # type: ignore
        self.texture_grid = self.spritesheet.get_texture_grid(
            (self.character_width, self.character_height),
            sheet_width // self.character_width,
            sum(self.animation_frames.values()),
        )
        self.textures: dict[MainCharacterState, list[tuple[arcade.Texture, arcade.Texture]]] = {
            state: self.get_textures(state) for state in MainCharacterState
        }

    @staticmethod
    def crop_transparent_image(texture: arcade.Texture, flipped: bool = False) -> arcade.Texture:
        copy = texture.image.copy()
        bbox = copy.getbbox()
        if not bbox:
            return texture
        copy = copy.crop((bbox[0], 0, bbox[2], copy.height))
        copy = copy.transpose(method=0) if flipped else copy
        return arcade.Texture(copy)

    def get_textures(
        self, state: MainCharacterState
    ) -> list[tuple[arcade.Texture, arcade.Texture]]:
        start = sum(self.animation_frames[s] for s in MainCharacterState if s < state)
        end = start + self.animation_frames[state]
        _textures: list[tuple[arcade.Texture, arcade.Texture]] = []
        for t in self.texture_grid[start:end]:
            _textures.append(
                (self.crop_transparent_image(t), self.crop_transparent_image(t, flipped=True))
            )
        return _textures

    def get_texture(self, flipped: bool = False) -> arcade.Texture:
        return self.textures[self.current_state][self.current_frame][flipped]

    def update(self) -> None:
        if (
            self.current_state == MainCharacterState.DEATH
            and self.current_frame == self.animation_frames[MainCharacterState.DEATH] - 1
        ):
            return
        self.current_frame = (self.current_frame + 1) % len(self.textures[self.current_state])

    def set_state(self, state: MainCharacterState) -> None:
        if self.current_state == state:
            return
        if state == MainCharacterState.JUMP:
            self.assets.jump_sound.play()
        if state == MainCharacterState.COMBO_ATTACK or state == MainCharacterState.DASH_ATTACK:
            self.assets.attack_sound.play()
        self.current_state = state
        self.current_frame = 0

    @property
    def center_x(self) -> float:
        return self.character_width // 2 * self.scale

    @property
    def center_y(self) -> float:
        return self.character_height // 2 * self.scale
