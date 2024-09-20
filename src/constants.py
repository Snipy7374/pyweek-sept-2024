from pathlib import Path

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Shadow of Doubt"

# Path to the game's root directory
try:
    ROOT_DIR = Path("src").resolve(strict=True)
except FileNotFoundError as e:
    raise RuntimeError(
        "Root dir not found. Perhaps try to run the project from root and not inside src."
    ) from e

# Path to the game's assets directory
# we don't need to be strict here as ROOT
# if the user is in the wrong dir they will already get
# the error from above
ASSETS_DIR = Path("assets").resolve()


TILE_SCALING = 3

MAX_LIGHTS = 100


# --- Constants for player movement and physics ---

# Character scale and position
CHARACTER_SCALING = 2.5
CHARACTER_POSITION = (128, 128)

# Gravity
GRAVITY = 2000

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.4
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.5

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied to move player left/right
PLAYER_MOVE_FORCE_ON_GROUND = 8000
PLAYER_MOVE_FORCE_IN_AIR = 2000
PLAYER_JUMP_IMPULSE = 2500

# --- Constants for player ends here ---


# --- Constants for enemy movement and physics ---

# Enemy scale
ENEMY_SCALING = 4
ENEMY_FRICTION = 0.5
ENEMY_MASS = 2.0

ARROW_MOVE_FORCE = 120
ARROW_MASS = 0.1
ARROW_GRAVITY = 10

SMALL_FIREBALL_MOVE_FORCE = 150
SMALL_FIREBALL_MASS = 0.1
SMALL_FIREBALL_GRAVITY = 15

LARGE_FIREBALL_MOVE_FORCE = 150
LARGE_FIREBALL_MASS = 0.1
LARGE_FIREBALL_GRAVITY = 15

ENEMY_PLAYER_DISTANCE_THRESHOLD = 300
ENEMY_ATTACK_DISTANCE_THRESHOLD = 100
ENEMY_ATTACK_PROBABILITY = 5

ENEMY_MOVE_FORCE = 500

# --- Constants for enemy ends here ---
