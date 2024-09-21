from __future__ import annotations

import enum
import math
import time
import typing as t

import arcade

from components.sprites.player import Player
from constants import (
    ARROW_GRAVITY,
    ARROW_MASS,
    ARROW_MOVE_FORCE,
    ASSETS_DIR,
    LARGE_FIREBALL_GRAVITY,
    LARGE_FIREBALL_MASS,
    LARGE_FIREBALL_MOVE_FORCE,
    SMALL_FIREBALL_GRAVITY,
    SMALL_FIREBALL_MASS,
    SMALL_FIREBALL_MOVE_FORCE,
)


class ProjectileTypes(enum.Enum):
    ARROW = "arrow"
    SMALL_FIREBALL = "small_fireball"
    LARGE_FIREBALL = "large_fireball"


class ProjectileAssets:
    projectile_width = 16
    projectile_height = 16
    path = ASSETS_DIR / "enemies" / "projectiles.png"
    textures: dict[ProjectileTypes, tuple[arcade.Texture, arcade.Texture]] = {}

    def __init__(self) -> None:
        self.spritesheet = arcade.load_spritesheet(self.path)
        sheet_width, sheet_height = self.spritesheet._image.size  # type: ignore
        self.texture_grid = self.spritesheet.get_texture_grid(
            (self.projectile_width, self.projectile_height),
            sheet_width // self.projectile_width,
            (sheet_width // self.projectile_width) * (sheet_height // self.projectile_height),
        )
        self.textures[ProjectileTypes.ARROW] = (
            self.texture_grid[0],
            self.texture_grid[0].flip_left_right(),
        )
        self.textures[ProjectileTypes.LARGE_FIREBALL] = (
            self.texture_grid[0 + sheet_width // self.projectile_width],
            self.texture_grid[0 + sheet_width // self.projectile_width].flip_left_right(),
        )
        self.textures[ProjectileTypes.SMALL_FIREBALL] = (
            self.texture_grid[1 + sheet_width // self.projectile_width],
            self.texture_grid[1 + sheet_width // self.projectile_width].flip_left_right(),
        )

    def get_texture(
        self, projectile_type: ProjectileTypes, flipped: bool = False
    ) -> arcade.Texture:
        return self.textures[projectile_type][flipped]


PROJECTILE_TEXTURES = ProjectileAssets()
PROJECTILE_STATS = {
    ProjectileTypes.ARROW: {
        "mass": ARROW_MASS,
        "force": ARROW_MOVE_FORCE,
        "gravity": ARROW_GRAVITY,
    },
    ProjectileTypes.SMALL_FIREBALL: {
        "mass": SMALL_FIREBALL_MASS,
        "force": SMALL_FIREBALL_MOVE_FORCE,
        "gravity": SMALL_FIREBALL_GRAVITY,
    },
    ProjectileTypes.LARGE_FIREBALL: {
        "mass": LARGE_FIREBALL_MASS,
        "force": LARGE_FIREBALL_MOVE_FORCE,
        "gravity": LARGE_FIREBALL_GRAVITY,
    },
}


class Projectile(arcade.Sprite):
    _projectile_type: ProjectileTypes
    _max_time_alive: float | None = None
    _power_map: dict[ProjectileTypes, float] = {
        ProjectileTypes.ARROW: 7.0,
        ProjectileTypes.SMALL_FIREBALL: 12.0,
        ProjectileTypes.LARGE_FIREBALL: 20.0,
    }

    def __init__(
        self,
        projectile_type: ProjectileTypes,
        angle: float,
        position: tuple[float, float],
        flipped: bool = False,
        max_time_alive: float | None = None,
        scale: float = 1.0,
    ) -> None:
        super().__init__(scale=scale)
        self._projectile_type = projectile_type
        self.angle = math.degrees(angle)
        self.position = position
        self.flipped = flipped
        self.texture = PROJECTILE_TEXTURES.get_texture(projectile_type, flipped=flipped)
        self._time_alive = 0
        self._max_time_alive = max_time_alive
        self._mass = PROJECTILE_STATS[projectile_type]["mass"]
        self._force = PROJECTILE_STATS[projectile_type]["force"]
        self._gravity = PROJECTILE_STATS[projectile_type]["gravity"]

    def update(self, delta_time: float) -> None:
        self._time_alive += delta_time
        if (
            self._max_time_alive and self._time_alive >= self._max_time_alive
        ) or self.center_y < -100:
            self.kill()
            return
        self.physics_engines[0].apply_force(
            self, (self._force, 0) if not self.flipped else (-self._force, 0)
        )

    def add_to_physics_engine(self, physics_engine: arcade.PymunkPhysicsEngine) -> None:
        physics_engine.add_sprite(
            self,
            mass=self._mass,
            damping=1.0,
            friction=0.6,
            collision_type="projectile",
            gravity=(0, -self._gravity),
            elasticity=0.9,
        )

        def wall_hit_handler(projectile: Projectile, *_: t.Any) -> None:
            projectile.kill()

        physics_engine.add_collision_handler("projectile", "wall", post_handler=wall_hit_handler)

        # projectile should not collide with enemies
        physics_engine.add_collision_handler("projectile", "enemy", begin_handler=lambda *_: False)  # type: ignore

        def player_hit_handler(projectile: Projectile, player: Player, *_: t.Any) -> None:
            projectile.kill()
            # player and projectile are facing each other and player is attacking, knockback effect
            if player.attacking and player._facing_right == projectile.flipped:  # type: ignore
                player.knockback = True
                return
            projectile_id = id(projectile)
            if projectile_id in player._hit_map and time.monotonic() - player._hit_map[projectile_id] < 0.5:  # type: ignore
                return
            player._hit_map[projectile_id] = time.monotonic()  # type: ignore
            player._damage_map[projectile_id] = self._power_map[self._projectile_type]  # type: ignore
            player.hurt = True

        physics_engine.add_collision_handler(
            "projectile", "player", post_handler=player_hit_handler
        )

        # projectile should not collide with other projectiles
        physics_engine.add_collision_handler("projectile", "projectile", begin_handler=lambda *_: False)  # type: ignore
