from __future__ import annotations

import arcade
import arcade.geometry

from assets import MainCharacter, MainCharacterState
from constants import (
    PLAYER_JUMP_IMPULSE,
    PLAYER_MOVE_FORCE_IN_AIR,
    PLAYER_MOVE_FORCE_ON_GROUND,
)


class Player(arcade.Sprite):
    _animation_debounce = 0.1
    _facing_right = True
    _jump_pressed = False
    _crouch_pressed = False
    _left_pressed = False
    _right_pressed = False
    _combo_attack_pressed = False

    def __init__(self, position: tuple[int, int], scale: float = 1):
        super().__init__(scale=scale)
        self.__scale = scale
        self.position = position
        self.spritesheet = MainCharacter(position=position, scale=scale)
        self.texture = self.spritesheet.get_texture()

    def update_animation(self, delta_time: float) -> None:
        self._animation_debounce -= delta_time
        if self._animation_debounce > 0:
            return
        self.spritesheet.update()
        self.texture = (
            self.spritesheet.get_texture()
            if self._facing_right
            else self.spritesheet.get_texture().flip_horizontally()
        )
        self.hit_box = arcade.hitbox.HitBox(
            self.texture.hit_box_points,
            position=self.position,
            scale=(self.__scale, self.__scale),
        )
        self._animation_debounce = 0.1

    def on_key_press(self, key: int, _: int) -> None:
        if key == arcade.key.LEFT:
            self._left_pressed = True
        elif key == arcade.key.RIGHT:
            self._right_pressed = True
        if key == arcade.key.SPACE:
            self._combo_attack_pressed = True
        if key == arcade.key.UP:
            self._jump_pressed = True
        if key == arcade.key.DOWN:
            self._crouch_pressed = True

    def on_key_release(self, key: int, _: int) -> None:
        if key == arcade.key.LEFT:
            self._left_pressed = False
        if key == arcade.key.RIGHT:
            self._right_pressed = False
        if key == arcade.key.UP:
            self._jump_pressed = False
        if key == arcade.key.DOWN:
            self._crouch_pressed = False

    def update(self, delta_time: float = 1 / 60) -> None:
        if not self.physics_engines:
            return
        is_on_ground = self.physics_engines[0].is_on_ground(self)
        move_force = PLAYER_MOVE_FORCE_ON_GROUND if is_on_ground else PLAYER_MOVE_FORCE_IN_AIR
        if self._left_pressed and not self._right_pressed and not self._combo_attack_pressed:
            self.physics_engines[0].apply_force(self, (-move_force, 0))
            self.physics_engines[0].set_friction(self, 0)
            self._facing_right = False
            if is_on_ground:
                self.spritesheet.set_state(MainCharacterState.RUN)
        elif self._right_pressed and not self._left_pressed and not self._combo_attack_pressed:
            self.physics_engines[0].apply_force(self, (move_force, 0))
            self.physics_engines[0].set_friction(self, 0)
            self._facing_right = True
            if is_on_ground:
                self.spritesheet.set_state(MainCharacterState.RUN)
        elif self._crouch_pressed and is_on_ground and not self._combo_attack_pressed:
            self.spritesheet.set_state(MainCharacterState.CROUCH)
            self.physics_engines[0].set_friction(self, 10.0)
            self.physics_engines[0].set_velocity(self, (0, 0))
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.CROUCH] - 2
            ):
                self.spritesheet.current_frame = 0

        if self._jump_pressed and is_on_ground and not self._combo_attack_pressed:
            self.physics_engines[0].apply_impulse(self, (0, PLAYER_JUMP_IMPULSE))
            self.spritesheet.set_state(MainCharacterState.JUMP)

        if self._combo_attack_pressed:
            self.spritesheet.set_state(MainCharacterState.COMBO_ATTACK)
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.COMBO_ATTACK] - 1
            ):
                self._combo_attack_pressed = False

        if not any(
            (
                self._left_pressed,
                self._right_pressed,
                self._jump_pressed,
                self._combo_attack_pressed,
                self._crouch_pressed,
            )
        ):
            self.physics_engines[0].set_friction(self, 10.0)
            if is_on_ground:
                self.spritesheet.set_state(MainCharacterState.IDLE)

        self.update_animation(delta_time)
