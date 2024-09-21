from __future__ import annotations

import enum
import pathlib
import typing

import arcade

from constants import ASSETS_DIR

from .projectiles import ProjectileTypes


class EnemyTypes(enum.IntEnum):
    ARCHER = 0
    ARCHMAGE = 1
    CAVALIER = 2
    CROSSBOW = 3
    HALBERD = 4
    HORSE = 5
    KING = 6
    MAGE = 7
    PRINCE = 8
    SHIELD = 9
    SPEAR = 10
    SWORD = 11


class EnemyStates(enum.IntEnum):
    ...


class ArcherStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    ATTACK_2 = 4
    HIT = 5
    DEATH = 6


class ArchmageStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    ATTACK_2 = 4
    SPELL = 5
    SPELL_2 = 6
    HIT = 7
    DEATH = 8


class CavalierStates(EnemyStates):
    IDLE = 0
    WALK = 1
    WALK_2 = 2
    JUMP = 3
    ATTACK = 4
    HIT = 5
    DEATH = 6


class CrossbowStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    ATTACK_2 = 4
    HIT = 5
    DEATH = 6


class HalberdStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    HIT = 4
    DEATH = 5


class HorseStates(EnemyStates):
    IDLE = 0
    WALK = 1
    WALK_2 = 2
    JUMP = 3
    ATTACK = 4
    HIT = 5
    DEATH = 6


class KingStates(EnemyStates):
    IDLE = 0
    IDLE_2 = 1
    WALK = 2
    JUMP = 3
    ATTACK = 4
    HIT = 5
    DEATH = 6


class MageStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    ATTACK_2 = 4
    SPELL = 5
    HIT = 6
    DEATH = 7


class PrinceStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    HIT = 4
    DEATH = 5


class ShieldStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    BLOCK = 4
    HIT = 5
    DEATH = 6


class SpearStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    HIT = 4
    DEATH = 5


class SwordStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    HIT = 4
    DEATH = 5


class AllStates(EnemyStates):
    IDLE = 0
    WALK = 1
    JUMP = 2
    ATTACK = 3
    ATTACK_2 = 4
    SPELL = 5
    SPELL_2 = 6
    BLOCK = 7
    HIT = 8
    DEATH = 9


class EnemyCharacter:
    attack_power: int
    hp: int
    character_width: int = 32
    character_height: int = 32
    animation_frames: dict[EnemyStates, int] = {}
    current_state: EnemyStates | None = None
    current_frame: int = 0
    states: typing.Type[AllStates] | None = None
    projectile_type: ProjectileTypes | None = None

    def __init__(
        self,
        position: tuple[int, int],
        path: str | pathlib.Path,
        scale: float = 1.0,
    ) -> None:
        self.path = path
        self.scale = scale
        self.position = position
        self.spritesheet = arcade.load_spritesheet(self.path)
        sheet_width, sheet_height = self.spritesheet._image.size  # type: ignore
        self.texture_grid = self.spritesheet.get_texture_grid(
            (self.character_width, self.character_height),
            sheet_width // self.character_width,
            (sheet_width // self.character_width) * (sheet_height // self.character_height),
        )
        self.textures: dict[EnemyStates, list[tuple[arcade.Texture, arcade.Texture]]] = {
            state: self.get_textures(state) for state in (self.states or [])
        }

    def get_textures(self, state: EnemyStates) -> list[tuple[arcade.Texture, arcade.Texture]]:
        sheet_width, _ = self.spritesheet._image.size  # type: ignore
        per_row = sheet_width // self.character_width
        start, end = per_row * state, (per_row * state) + per_row
        return [
            (t, t.flip_left_right())
            for t in self.texture_grid[start:end][: self.animation_frames[state]]
        ]

    def get_texture(self, flipped: bool = False) -> arcade.Texture:
        assert self.current_state is not None, "Current state is not set"
        return self.textures[self.current_state][self.current_frame][flipped]

    def update(self) -> None:
        assert self.current_state is not None, "Current state is not set"
        assert self.states is not None, "States is not set"
        if (
            self.current_state == self.states.DEATH
            and self.current_frame == self.animation_frames[self.states.DEATH] - 1
        ):
            return
        if (
            self.current_state == self.states.JUMP
            and self.current_frame == self.animation_frames[self.states.JUMP] - 1
        ):
            return
        self.current_frame = (self.current_frame + 1) % len(self.textures[self.current_state])

    def set_state(self, state: EnemyStates) -> None:
        if self.current_state == state:
            return
        self.current_state = state
        self.current_frame = 0

    def is_done(self) -> bool:
        assert self.current_state is not None, "Current state is not set"
        return self.current_frame == self.animation_frames[self.current_state] - 1

    @property
    def all_states(self) -> typing.Type[AllStates]:
        assert self.states is not None, "States is not set"
        return self.states

    @classmethod
    def from_type(cls, enemy_type: EnemyTypes, position: tuple[int, int]) -> EnemyCharacter:
        _path = ASSETS_DIR / "enemies" / f"{enemy_type.name.lower()}.png"
        _enemy_map = {
            EnemyTypes.ARCHER: Archer,
            EnemyTypes.ARCHMAGE: Archmage,
            EnemyTypes.CAVALIER: Cavalier,
            EnemyTypes.CROSSBOW: Crossbow,
            EnemyTypes.HALBERD: Halberd,
            EnemyTypes.HORSE: Horse,
            EnemyTypes.KING: King,
            EnemyTypes.MAGE: Mage,
            EnemyTypes.PRINCE: Prince,
            EnemyTypes.SHIELD: Shield,
            EnemyTypes.SPEAR: Spear,
            EnemyTypes.SWORD: Sword,
        }
        return _enemy_map[enemy_type](position, _path)


class Archer(EnemyCharacter):
    animation_frames = {
        ArcherStates.IDLE: 4,
        ArcherStates.WALK: 6,
        ArcherStates.JUMP: 3,
        ArcherStates.ATTACK: 11,
        ArcherStates.ATTACK_2: 6,
        ArcherStates.HIT: 3,
        ArcherStates.DEATH: 4,
    }
    current_state = ArcherStates.IDLE
    states = ArcherStates  # type: ignore
    projectile_type = ProjectileTypes.ARROW
    hp = 80
    attack_power = 5


class Archmage(EnemyCharacter):
    animation_frames = {
        ArchmageStates.IDLE: 4,
        ArchmageStates.WALK: 6,
        ArchmageStates.JUMP: 3,
        ArchmageStates.ATTACK: 11,
        ArchmageStates.ATTACK_2: 9,
        ArchmageStates.SPELL: 9,
        ArchmageStates.SPELL_2: 10,
        ArchmageStates.HIT: 2,
        ArchmageStates.DEATH: 9,
    }
    current_state = ArchmageStates.IDLE
    states = ArchmageStates  # type: ignore
    projectile_type = ProjectileTypes.LARGE_FIREBALL
    hp = 130
    attack_power = 7


class Cavalier(EnemyCharacter):
    animation_frames = {
        CavalierStates.IDLE: 8,
        CavalierStates.WALK: 6,
        CavalierStates.WALK_2: 6,
        CavalierStates.JUMP: 3,
        CavalierStates.ATTACK: 7,
        CavalierStates.HIT: 2,
        CavalierStates.DEATH: 6,
    }
    current_state = CavalierStates.IDLE
    states = CavalierStates  # type: ignore
    hp = 100
    attack_power = 6


class Crossbow(EnemyCharacter):
    animation_frames = {
        CrossbowStates.IDLE: 4,
        CrossbowStates.WALK: 6,
        CrossbowStates.JUMP: 3,
        CrossbowStates.ATTACK: 10,
        CrossbowStates.ATTACK_2: 4,
        CrossbowStates.HIT: 3,
        CrossbowStates.DEATH: 4,
    }
    current_state = CrossbowStates.IDLE
    states = CrossbowStates  # type: ignore
    projectile_type = ProjectileTypes.ARROW
    hp = 90
    attack_power = 1


class Halberd(EnemyCharacter):
    animation_frames = {
        HalberdStates.IDLE: 4,
        HalberdStates.WALK: 6,
        HalberdStates.JUMP: 3,
        HalberdStates.ATTACK: 6,
        HalberdStates.HIT: 3,
        HalberdStates.DEATH: 5,
    }
    current_state = HalberdStates.IDLE
    states = HalberdStates  # type: ignore
    hp = 110
    attack_power = 10


class Horse(EnemyCharacter):
    animation_frames = {
        HorseStates.IDLE: 8,
        HorseStates.WALK: 6,
        HorseStates.WALK_2: 6,
        HorseStates.JUMP: 3,
        HorseStates.ATTACK: 7,
        HorseStates.HIT: 2,
        HorseStates.DEATH: 6,
    }
    current_state = HorseStates.IDLE
    states = HorseStates  # type: ignore
    hp = 120
    attack_power = 8


class King(EnemyCharacter):
    animation_frames = {
        KingStates.IDLE: 4,
        KingStates.IDLE_2: 5,
        KingStates.WALK: 6,
        KingStates.JUMP: 5,
        KingStates.ATTACK: 10,
        KingStates.HIT: 3,
        KingStates.DEATH: 6,
    }
    current_state = KingStates.IDLE
    states = KingStates  # type: ignore
    hp = 150
    attack_power = 12


class Mage(EnemyCharacter):
    animation_frames = {
        MageStates.IDLE: 4,
        MageStates.WALK: 6,
        MageStates.JUMP: 3,
        MageStates.ATTACK: 11,
        MageStates.ATTACK_2: 9,
        MageStates.SPELL: 9,
        MageStates.HIT: 2,
        MageStates.DEATH: 9,
    }
    current_state = MageStates.IDLE
    states = MageStates  # type: ignore
    projectile_type = ProjectileTypes.SMALL_FIREBALL
    hp = 120
    attack_power = 3


class Prince(EnemyCharacter):
    animation_frames = {
        PrinceStates.IDLE: 4,
        PrinceStates.WALK: 6,
        PrinceStates.JUMP: 5,
        PrinceStates.ATTACK: 6,
        PrinceStates.HIT: 3,
        PrinceStates.DEATH: 6,
    }
    current_state = PrinceStates.IDLE
    states = PrinceStates  # type: ignore
    hp = 100
    attack_power = 6


class Shield(EnemyCharacter):
    animation_frames = {
        ShieldStates.IDLE: 4,
        ShieldStates.WALK: 6,
        ShieldStates.JUMP: 3,
        ShieldStates.ATTACK: 6,
        ShieldStates.BLOCK: 6,
        ShieldStates.HIT: 3,
        ShieldStates.DEATH: 4,
    }
    current_state = ShieldStates.IDLE
    states = ShieldStates  # type: ignore
    hp = 180
    attack_power = 9


class Spear(EnemyCharacter):
    animation_frames = {
        SpearStates.IDLE: 4,
        SpearStates.WALK: 6,
        SpearStates.JUMP: 3,
        SpearStates.ATTACK: 7,
        SpearStates.HIT: 3,
        SpearStates.DEATH: 5,
    }
    current_state = SpearStates.IDLE
    states = SpearStates  # type: ignore
    hp = 100
    attack_power = 15


class Sword(EnemyCharacter):
    animation_frames = {
        SwordStates.IDLE: 4,
        SwordStates.WALK: 6,
        SwordStates.JUMP: 3,
        SwordStates.ATTACK: 6,
        SwordStates.HIT: 3,
        SwordStates.DEATH: 4,
    }
    current_state = SwordStates.IDLE
    states = SwordStates  # type: ignore
    hp = 90
    attack_power = 18
