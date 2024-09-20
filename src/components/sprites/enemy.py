from __future__ import annotations

import math
import random
import typing as t

import arcade

from components.utils.enemy import EnemyCharacter, EnemyTypes
from components.utils.projectiles import Projectile
from constants import (
    ENEMY_PLAYER_DISTANCE_THRESHOLD,
    ENEMY_ATTACK_DISTANCE_THRESHOLD,
    ENEMY_ATTACK_PROBABILITY,
    ENEMY_MOVE_FORCE,
)


class Enemy(arcade.Sprite):
    _animation_debounce = 0.1
    _facing_right = False

    # variables for idle animation
    _walk_around = False
    _walk_around_time = 0
    _walk_around_velocity = 0
    _switch_time = 0

    _jump_around = False
    _jump_around_time = 0
    _jump_around_velocity = 0
    _jump_time = 0
    # variables for idle animation end here

    _attacking = False
    _hurt = False
    _dead = False

    def __init__(
        self,
        enemy_type: EnemyTypes,
        scene: arcade.Scene,
        position: tuple[int, int],
        scale: float = 1.0,
        properties: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(scale=scale)
        self.properties = properties or {}
        self._facing_right = self.properties.get("facing_right", False)
        self._walk_around = self.properties.get("walk_around", False)
        self._walk_around_time = self.properties.get("walk_around_time", 3.0)
        self._walk_around_velocity = self.properties.get("walk_around_velocity", 200)
        self._switch_time = self._walk_around_time
        self._jump_around = self.properties.get("jump_around", False)
        self._jump_around_time = self.properties.get("jump_around_time", 3.0)
        self._jump_around_velocity = self.properties.get("jump_around_velocity", 400)
        self._jump_time = self._jump_around_time
        self.scene = scene
        self.position = position
        self.spritesheet = EnemyCharacter.from_type(enemy_type, position)
        self.texture = self.spritesheet.get_texture()
        self.attack_states = [self.spritesheet.all_states.ATTACK]
        if hasattr(self.spritesheet.all_states, "ATTACK_2"):
            self.attack_states.append(self.spritesheet.all_states.ATTACK_2)
        if hasattr(self.spritesheet.all_states, "SPELL"):
            self.attack_states.append(self.spritesheet.all_states.SPELL)
        if hasattr(self.spritesheet.all_states, "SPELL_2"):
            self.attack_states.append(self.spritesheet.all_states.SPELL_2)

    def update_animation(self, delta_time: float) -> None:
        self._animation_debounce -= delta_time
        if self._animation_debounce > 0:
            return
        self.spritesheet.update()
        self.texture = self.spritesheet.get_texture(flipped=not self._facing_right)
        self.hit_box = arcade.hitbox.RotatableHitBox(
            self.texture.hit_box_points,
            position=self._position,
            scale=self._scale,
            angle=self._angle,
        )
        self._animation_debounce = 0.1

    def reset(self, scene: arcade.Scene) -> None:
        self.scene = scene
        self._facing_right = True
        self._animation_debounce = 0.1

    def attack(self) -> None:
        if self._attacking and self.spritesheet.current_state in self.attack_states:
            return
        self.physics_engines[0].set_friction(self, 1.0)
        self.physics_engines[0].set_velocity(self, (0, 0))
        self.spritesheet.set_state(random.choice(self.attack_states))
        player = self.scene.get_sprite_list("Player")[0]
        if self.spritesheet.projectile_type is not None:
            player_pos = player.position
            enemy_pos = self.position

            if player_pos[0] > enemy_pos[0]:
                angle = math.atan2(player_pos[1] - enemy_pos[1], player_pos[0] - enemy_pos[0])
            else:
                angle = math.atan2(enemy_pos[1] - player_pos[1], enemy_pos[0] - player_pos[0])

            size_x = 48 if player_pos[0] > enemy_pos[0] else -48
            x = enemy_pos[0] + size_x * math.cos(angle)
            y = enemy_pos[1] - 16

            flipped = player_pos[0] < enemy_pos[0]

            projectile = Projectile(
                self.spritesheet.projectile_type, angle, (x, y), scale=3.5, flipped=flipped
            )
            self.scene.add_sprite("Projectiles", projectile)
            projectile.add_to_physics_engine(self.physics_engines[0])

    def update(self, delta_time: float = 1 / 60) -> None:
        if self._dead:
            self.spritesheet.set_state(self.spritesheet.all_states.DEATH)
            self.physics_engines[0].set_friction(self, 10.0)
            if self.spritesheet.is_done():
                self.kill()
            return
        if self._hurt:
            self.spritesheet.set_state(self.spritesheet.all_states.HIT)
            if self.spritesheet.is_done():
                self._hurt = False
                self.physics_engines[0].set_friction(self, 1.0)
                self.spritesheet.set_state(self.spritesheet.all_states.IDLE)
            return
        if self._attacking:
            self.attack()
            if self.spritesheet.is_done():
                self._attacking = False
                self.physics_engines[0].set_friction(self, 1.0)
                self.spritesheet.set_state(self.spritesheet.all_states.IDLE)
            return
        if self.center_y < -100:
            self.kill()
            return

        on_ground = self.physics_engines[0].is_on_ground(self)
        plater = self.scene.get_sprite_list("Player")[0]
        player_pos = plater.position
        enemy_pos = self.position

        if abs(player_pos[0] - enemy_pos[0]) < ENEMY_PLAYER_DISTANCE_THRESHOLD:
            if abs(player_pos[0] - enemy_pos[0]) > ENEMY_PLAYER_DISTANCE_THRESHOLD:
                self._attacking = False
                return

            self._facing_right = player_pos[0] > enemy_pos[0]

            if (
                on_ground
                and self.spritesheet.projectile_type is None
                and abs(player_pos[0] - enemy_pos[0]) > ENEMY_ATTACK_DISTANCE_THRESHOLD
            ):
                vx = ENEMY_MOVE_FORCE if self._facing_right else -ENEMY_MOVE_FORCE
                self.physics_engines[0].set_friction(self, 0.0)
                self.physics_engines[0].apply_force(self, (vx, 0))
                self.spritesheet.set_state(self.spritesheet.all_states.WALK)
                return

            if not on_ground:
                self._attacking = False
                return

            self._attacking = (
                random.randint(0, 100) < ENEMY_ATTACK_PROBABILITY
                or abs(player_pos[0] - enemy_pos[0]) < 30
            )
            if self._attacking:
                return

            if self.spritesheet.projectile_type is None:
                vx = ENEMY_MOVE_FORCE if self._facing_right else -ENEMY_MOVE_FORCE
                self.physics_engines[0].set_friction(self, 0.0)
                self.physics_engines[0].apply_force(self, (vx, 0))
                self.spritesheet.set_state(self.spritesheet.all_states.WALK)
                return

            return

        if self._walk_around and on_ground:
            self._switch_time -= delta_time
            if self._switch_time <= 0:
                self._switch_time = self._walk_around_time
                self._facing_right = not self._facing_right
            vx = self._walk_around_velocity if self._facing_right else -self._walk_around_velocity
            self.physics_engines[0].set_friction(self, 0.0)
            self.physics_engines[0].set_velocity(self, (vx, 0))
            self.spritesheet.set_state(self.spritesheet.all_states.WALK)
        elif self._jump_around:
            self._jump_time -= delta_time
            if self._jump_time <= 0 and on_ground:
                self._jump_time = self._jump_around_time
                self.physics_engines[0].apply_impulse(self, (0, self._jump_around_velocity))
                self.spritesheet.set_state(self.spritesheet.all_states.JUMP)
            elif on_ground:
                self.physics_engines[0].set_friction(self, 1.0)
                self.spritesheet.set_state(self.spritesheet.all_states.IDLE)
        else:
            self.physics_engines[0].set_friction(self, 1.0)
            self.spritesheet.set_state(self.spritesheet.all_states.IDLE)

    @property
    def attacking(self) -> bool:
        return self._attacking

    @property
    def hurt(self) -> bool:
        return self._hurt

    @hurt.setter
    def hurt(self, value: bool) -> None:
        self._hurt = value
        if self._hurt:
            self._attacking = False

    @property
    def dead(self) -> bool:
        return self._dead

    @dead.setter
    def dead(self, value: bool) -> None:
        self._dead = value
        if self._dead:
            self._attacking = False
            self._hurt = False
            self.physics_engines[0].set_friction(self, 10.0)
