from __future__ import annotations

import typing as t

import arcade

from components.utils.enemy import EnemyCharacter, EnemyTypes


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

    def update(self, delta_time: float = 1 / 60) -> None:
        on_ground = self.physics_engines[0].is_on_ground(self)
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
                self.physics_engines[0].set_friction(self, 10.0)
                self.spritesheet.set_state(self.spritesheet.all_states.IDLE)
        else:
            self.physics_engines[0].set_friction(self, 10.0)
            self.spritesheet.set_state(self.spritesheet.all_states.IDLE)
