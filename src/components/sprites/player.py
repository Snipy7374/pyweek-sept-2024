from __future__ import annotations

import time
import random
import arcade

from components.utils.player import MainCharacter, MainCharacterState
from components.utils.bars import Bar, BarColors, BarIcons
from constants import (
    ASSETS_DIR,
    CHARACTER_POSITION,
    PLAYER_JUMP_IMPULSE,
    PLAYER_MOVE_FORCE_IN_AIR,
    PLAYER_MOVE_FORCE_ON_GROUND,
    PLAYER_SMALL_JUMP_IMPULSE,
)


MAX_HEALTH = 200
MAX_STAMINA = 50
MIN_ATTACK_VALUE = 10
MAX_ATTACK_VALUE = 20


class Player(arcade.Sprite):
    _hp = MAX_HEALTH
    _stamina = MAX_STAMINA
    _animation_debounce = 0.1
    _score = 0
    _hurt = False
    _dead = False
    _small_jump = False
    _knockback = False
    _facing_right = True
    _jump_pressed = False
    _crouch_pressed = False
    _left_pressed = False
    _right_pressed = False
    _combo_attack_pressed = False
    _dash_pressed = False
    _dash_attack_pressed = False
    _score_text: arcade.Text | None = None
    _health_bar = Bar(BarColors.RED, BarIcons.HEALTH, MAX_HEALTH, MAX_HEALTH, scale=0.06)
    _stamina_bar = Bar(BarColors.YELLOW, BarIcons.STAMINA, MAX_STAMINA, MAX_STAMINA, scale=0.06)
    _damage_map: dict[int, int] = {}
    _hit_map: dict[int, float] = {}
    _last_hit_time: float | None = None
    _last_stamina_time: float | None = None
    _stamina_usage_map = {
        MainCharacterState.COMBO_ATTACK: 10,
        MainCharacterState.DASH: 5,
        MainCharacterState.DASH_ATTACK: 15,
        MainCharacterState.JUMP: 5,
    }

    def __init__(self, scene: arcade.Scene, position: tuple[int, int], scale: float = 1) -> None:
        super().__init__(scale=scale)
        self.scene = scene
        self.position = position
        self.spritesheet = MainCharacter(position=position, scale=scale)
        self.texture = self.spritesheet.get_texture(flipped=not self._facing_right)

    def update_score(self):
        gold_hit_list = arcade.check_for_collision_with_list(self, self.scene["Gold"])
        for gold in gold_hit_list:
            gold.remove_from_sprite_lists()
            self._score += gold.properties["value"]
            self.spritesheet.assets.coin_collect_sound.play()

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
        self._score = 0
        self._dead = False
        self._facing_right = True
        self._jump_pressed = False
        self._crouch_pressed = False
        self._left_pressed = False
        self._right_pressed = False
        self._combo_attack_pressed = False
        self._dash_pressed = False
        self._dash_attack_pressed = False
        self.position = CHARACTER_POSITION
        self.spritesheet.set_state(MainCharacterState.IDLE)
        self.physics_engines[0].set_friction(self, 10.0)
        self.physics_engines[0].set_velocity(self, (0, 0))

    def on_key_press(self, key: int, _: int) -> None:
        if key == arcade.key.J:
            self._small_jump = not self._small_jump
        if key == arcade.key.LEFT or key == arcade.key.A:
            self._left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self._right_pressed = True
        if key == arcade.key.SPACE:
            self._combo_attack_pressed = True
        if key == arcade.key.UP or key == arcade.key.W:
            self._jump_pressed = True
        if key == arcade.key.DOWN or key == arcade.key.S:
            self._crouch_pressed = True
        if key == arcade.key.LSHIFT:
            self._dash_pressed = True
        if key == arcade.key.LCTRL:
            self._dash_attack_pressed = True

    def on_key_release(self, key: int, _: int) -> None:
        if key == arcade.key.LEFT or key == arcade.key.A:
            self._left_pressed = False
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self._right_pressed = False
        if key == arcade.key.UP or key == arcade.key.W:
            self._jump_pressed = False
        if key == arcade.key.DOWN or key == arcade.key.S:
            self._crouch_pressed = False

    def update(self, _: float = 1 / 60) -> None:
        self.scene["Bars"][0].position = self.position[0], self.position[1] + 80
        self.scene["Bars"][1].position = self.position[0], self.position[1] + 45
        if not self.physics_engines or self.dead:
            return
        if (
            self._last_hit_time is not None
            and time.monotonic() - self._last_hit_time > 2.0
            and self._hp < MAX_HEALTH
            and not self._hurt
        ):
            self._hp = min(self._hp + 0.4, MAX_HEALTH)
            self._health_bar.value = int(max(self._hp, 0))
            self.scene["Bars"][0].texture = self._health_bar.texture
        if (
            self._last_stamina_time is not None
            and time.monotonic() - self._last_stamina_time > 1.0
            and self._stamina < MAX_STAMINA
        ):
            self._stamina = min(self._stamina + 0.2, MAX_STAMINA)
            self._stamina_bar.value = int(max(self._stamina, 0))
            self.scene["Bars"][1].texture = self._stamina_bar.texture
        if self._knockback:
            self.physics_engines[0].set_friction(self, 0.0)
            move_force = (
                PLAYER_MOVE_FORCE_ON_GROUND
                if self.physics_engines[0].is_on_ground(self)
                else PLAYER_MOVE_FORCE_IN_AIR
            )
            force = move_force * 3 if not self._facing_right else -move_force * 3
            self.physics_engines[0].apply_force(self, (force, force))
            self._knockback = False
            return
        if self._hurt:
            self.physics_engines[0].set_friction(self, 10.0)
            self.spritesheet.set_state(MainCharacterState.HURT)
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.HURT] - 1
            ):
                self._hurt = False
                self._hp -= sum(self._damage_map.values())
                self._last_hit_time = time.monotonic()
                if self._hp <= 0:
                    self.dead = True
                    return
                self._damage_map = {}
                self._health_bar.value = int(max(self._hp, 0))
                self.scene["Bars"][0].texture = self._health_bar.texture
                self.spritesheet.set_state(MainCharacterState.IDLE)
            else:
                return
        if self.center_y < -100:
            self.dead = True
            return
        is_on_ground = self.physics_engines[0].is_on_ground(self)
        move_force = PLAYER_MOVE_FORCE_ON_GROUND if is_on_ground else PLAYER_MOVE_FORCE_IN_AIR
        if (
            self._left_pressed
            and not self._right_pressed
            and not self._combo_attack_pressed
            and not self._dash_attack_pressed
        ):
            self.physics_engines[0].apply_force(self, (-move_force, 0))
            self.physics_engines[0].set_friction(self, 0)
            self._facing_right = False
            if is_on_ground:
                if self._dash_pressed:
                    self.physics_engines[0].apply_force(self, (-move_force * 3, 0))
                    self.spritesheet.set_state(MainCharacterState.DASH)
                else:
                    self.spritesheet.set_state(MainCharacterState.RUN)
        elif (
            self._right_pressed
            and not self._left_pressed
            and not self._combo_attack_pressed
            and not self._dash_attack_pressed
        ):
            self.physics_engines[0].apply_force(self, (move_force, 0))
            self.physics_engines[0].set_friction(self, 0)
            self._facing_right = True
            if is_on_ground:
                if self._dash_pressed:
                    self.physics_engines[0].apply_force(self, (move_force * 3, 0))
                    self.spritesheet.set_state(MainCharacterState.DASH)
                else:
                    self.spritesheet.set_state(MainCharacterState.RUN)
        elif (
            self._crouch_pressed
            and is_on_ground
            and not self._combo_attack_pressed
            and not self._dash_attack_pressed
        ):
            self.spritesheet.set_state(MainCharacterState.CROUCH)
            self.physics_engines[0].set_friction(self, 10.0)
            self.physics_engines[0].set_velocity(self, (0, 0))
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.CROUCH] - 2
            ):
                self.spritesheet.current_frame = 0

        if (
            self._jump_pressed
            and self.stamina > self._stamina_usage_map[MainCharacterState.JUMP]
            and is_on_ground
            and not self._combo_attack_pressed
            and not self._dash_attack_pressed
        ):
            self.physics_engines[0].apply_impulse(
                self,
                (0, PLAYER_JUMP_IMPULSE if not self._small_jump else PLAYER_SMALL_JUMP_IMPULSE),
            )
            self.spritesheet.set_state(MainCharacterState.JUMP)
            if self._last_stamina_time is None or time.monotonic() - self._last_stamina_time > 0.5:
                self.stamina = max(
                    self._stamina - self._stamina_usage_map[MainCharacterState.JUMP], 0
                )

        if (
            self._combo_attack_pressed
            and not self._dash_attack_pressed
            and self.stamina > self._stamina_usage_map[MainCharacterState.COMBO_ATTACK]
        ):
            self.spritesheet.set_state(MainCharacterState.COMBO_ATTACK)
            self.physics_engines[0].set_friction(self, 1.0)
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.COMBO_ATTACK] - 1
            ):
                self._combo_attack_pressed = False
                self.stamina = max(
                    self._stamina - self._stamina_usage_map[MainCharacterState.COMBO_ATTACK], 0
                )

        if (
            self._dash_attack_pressed
            and not self._combo_attack_pressed
            and self.stamina > self._stamina_usage_map[MainCharacterState.DASH_ATTACK]
        ):
            self.physics_engines[0].set_friction(self, 10.0)
            self.spritesheet.set_state(MainCharacterState.DASH_ATTACK)
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.DASH_ATTACK] - 1
            ):
                self._dash_attack_pressed = False
                self.stamina = max(
                    self._stamina - self._stamina_usage_map[MainCharacterState.DASH_ATTACK], 0
                )

        if (
            self._dash_pressed
            and not self._combo_attack_pressed
            and not self._dash_attack_pressed
            and self.stamina > self._stamina_usage_map[MainCharacterState.DASH]
        ):
            if is_on_ground:
                self.physics_engines[0].set_friction(self, 0)
                force = move_force if self._facing_right else -move_force
                self.physics_engines[0].apply_force(self, (force, 0.7))
            self.spritesheet.set_state(MainCharacterState.DASH)
            if (
                self.spritesheet.current_frame
                == self.spritesheet.animation_frames[MainCharacterState.DASH] - 1
            ):
                self._dash_pressed = False
                self.physics_engines[0].set_friction(self, 10.0)
                self.stamina = max(
                    self._stamina - self._stamina_usage_map[MainCharacterState.DASH], 0
                )

        if not any(
            (
                self._left_pressed,
                self._right_pressed,
                self._jump_pressed,
                self._combo_attack_pressed,
                self._crouch_pressed,
                self._dash_pressed,
                self._dash_attack_pressed,
            )
        ):
            self.physics_engines[0].set_friction(self, 10.0)
            if is_on_ground:
                self.spritesheet.set_state(MainCharacterState.IDLE)

        self.update_score()

    @property
    def dead(self) -> bool:
        return self._dead

    @dead.setter
    def dead(self, value: bool) -> None:
        self._dead = value
        if self._dead:
            self.spritesheet.set_state(MainCharacterState.DEATH)
            self.physics_engines[0].set_friction(self, 10.0)
            self.physics_engines[0].set_velocity(self, (0, 0))

    @property
    def score(self) -> arcade.Text:
        if not self._score_text:
            window = arcade.get_window()
            arcade.load_font(ASSETS_DIR / "fonts" / "Alagard.ttf")
            self._score_text = arcade.Text(
                f"Score: {self._score}",
                x=window.width - 150,
                y=window.height - 40,
                color=arcade.color.WHITE,
                font_size=32,
                anchor_x="center",
                anchor_y="center",
                font_name="Alagard",
            )
        self._score_text.text = f"Score: {self._score}"
        return self._score_text

    @property
    def health_bar(self):
        sprite = arcade.Sprite()
        sprite.texture = self._health_bar.texture
        sprite.position = self.position[0], self.position[1] + 80
        return sprite

    @property
    def stamina_bar(self):
        sprite = arcade.Sprite()
        sprite.texture = self._stamina_bar.texture
        sprite.position = self.position[0], self.position[1] + 45
        return sprite

    @property
    def attacking(self) -> bool:
        return self._combo_attack_pressed or self._dash_attack_pressed

    @property
    def hurt(self) -> bool:
        return self._hurt

    @hurt.setter
    def hurt(self, value: bool) -> None:
        self._hurt = value
        if self._hurt:
            self._combo_attack_pressed = False
            self._dash_attack_pressed = False
            self._dash_pressed = False
            self._crouch_pressed = False

    @property
    def knockback(self) -> bool:
        return self._knockback

    @knockback.setter
    def knockback(self, value: bool) -> None:
        self._knockback = value

    @property
    def stamina(self) -> int | float:
        return self._stamina

    @stamina.setter
    def stamina(self, value: float | int) -> None:
        self._stamina = value
        self._last_stamina_time = time.monotonic()
        self._stamina_bar.value = int(max(self._stamina, 0))
        self.scene["Bars"][1].texture = self._stamina_bar.texture

    @property
    def attack_power(self) -> int:
        return random.randint(MIN_ATTACK_VALUE, MAX_ATTACK_VALUE)

    @property
    def is_dead(self) -> bool:
        if (
            self._dead
            and self.spritesheet.current_frame
            == self.spritesheet.animation_frames[MainCharacterState.DEATH] - 1
        ):
            return True
        return False
