import random
from .base_ai import BaseAI
from .difficulty import Difficulty, get_depth
from .heuristic_advanced import advanced_eval
from .heuristic_basic import basic_eval
from game.game_state import GameState
import chess

class MinimaxAI(BaseAI):
    def __init__(self, color: str, difficulty: Difficulty = Difficulty.HARD, use_advanced=True):
        super().__init__(color, difficulty)
        self.max_depth = get_depth(difficulty)
        self.use_advanced = use_advanced
        self._eval_cache = {}

    def choose_move(self, gs: GameState):
        moves = self._generate_all_moves(gs, self.color)
        if not moves:
            return None

        best_score = -1e9
        best_moves = []

        for mv in moves:
            clone = gs.clone()
            try:
                clone.move(mv[0], mv[1])
            except ValueError:
                continue
            score = self._minimax(clone, self.max_depth-1, -1e9, 1e9, False)
            if score > best_score:
                best_score = score
                best_moves = [mv]
            elif score == best_score:
                best_moves.append(mv)

        return random.choice(best_moves) if best_moves else None

    def _minimax(self, gs: GameState, depth, alpha, beta, maximizing):
        if depth == 0:
            return self._evaluate(gs)

        color_to_move = gs.turn
        moves = self._generate_all_moves(gs, color_to_move)
        if not moves:
            return -1e6 if color_to_move == self.color else 1e6

        if maximizing:
            value = -1e9
            for mv in moves:
                clone = gs.clone()
                try:
                    clone.move(mv[0], mv[1])
                except ValueError:
                    continue
                value = max(value, self._minimax(clone, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = 1e9
            for mv in moves:
                clone = gs.clone()
                try:
                    clone.move(mv[0], mv[1])
                except ValueError:
                    continue
                value = min(value, self._minimax(clone, depth-1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def _evaluate(self, gs: GameState):
        h = tuple((p.true_type, p.color, p.isFaceDown) if p else None for row in gs.board for p in row)
        if h in self._eval_cache:
            return self._eval_cache[h]

        score = advanced_eval(gs, self.color) if self.use_advanced else basic_eval(gs, self.color)
        self._eval_cache[h] = score
        return score

    def _generate_all_moves(self, gs: GameState, color):
        moves = []

        for r in range(8):
            for c in range(8):
                piece = gs.get_piece(r, c)
                if piece and piece.color == color:
                    # tạo board riêng cho quân này để face-down dùng start_type
                    board = gs.to_chessboard(sr=r, sc=c)
                    board.turn = chess.WHITE if color=='w' else chess.BLACK
                    for m in board.legal_moves:
                        fr, fc = 7 - (m.from_square // 8), m.from_square % 8
                        tr, tc = 7 - (m.to_square // 8), m.to_square % 8
                        if (fr, fc) == (r, c):
                            start_sq = f"{chr(fc + ord('a'))}{8 - fr}"
                            end_sq = f"{chr(tc + ord('a'))}{8 - tr}"
                            moves.append((start_sq, end_sq))
        return moves
