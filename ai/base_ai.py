# ai/base_ai.py
from abc import ABC, abstractmethod

class BaseAI(ABC):
    def __init__(self, color: str, difficulty=None):
        """
        color: 'w' or 'b' - which side the AI plays
        difficulty: object from difficulty.py (optional)
        """
        self.color = color
        self.difficulty = difficulty

    @abstractmethod
    def choose_move(self, game_state):
        # """
        # Return a tuple (start_square, end_square) like ('e2','e4'), or None if no move.
        # """
        pass
