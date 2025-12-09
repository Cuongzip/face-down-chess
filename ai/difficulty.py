# ai/difficulty.py
from enum import Enum

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

# map difficulty -> search depth (plies)
DEPTH_MAP = {
    Difficulty.EASY: 1,    # 1-ply (very fast, tactical)
    Difficulty.MEDIUM: 3,  # 3-ply (reasonable)
    Difficulty.HARD: 4     # 4-ply (slower but stronger)
}

def get_depth(diff):
    return DEPTH_MAP.get(diff, 3)
