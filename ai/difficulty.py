# ai/difficulty.py
from enum import Enum


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


# map difficulty -> search depth (plies)
DEPTH_MAP = {
    Difficulty.EASY: 1,
    Difficulty.MEDIUM: 2,
    Difficulty.HARD: 3
}


def get_depth(diff):
    return DEPTH_MAP.get(diff, 3)
