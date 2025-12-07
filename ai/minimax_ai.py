import chess
import random
from .base_ai import BaseAI
from .difficulty import Difficulty, get_depth
from .heuristic_basic import basic_eval
from .heuristic_advanced import advanced_eval
from game.board_converter import BoardConverter

class MinimaxAI(BaseAI):
    def __init__(self, color: str, difficulty: Difficulty = Difficulty.MEDIUM, use_advanced=True):
        super().__init__(color, difficulty)
        self.max_depth = get_depth(difficulty)
        self.use_advanced = use_advanced

    # -----------------------------------------------------
    # MAIN API
    # -----------------------------------------------------
    def choose_move(self, game_state):
        moves = self._generate_all_moves(game_state, self.color)
        if not moves:
            return None

        best_score = -10**9
        best_moves = []

        for mv in moves:
            gs_clone = self._clone_game_state(game_state)

            try:
                gs_clone.move(mv[0], mv[1])     # turn automatically changes
            except Exception:
                continue

            score = self._minimax(gs_clone, self.max_depth - 1,
                                  -10**9, 10**9, maximizing=False)

            if score > best_score:
                best_score = score
                best_moves = [mv]
            elif score == best_score:
                best_moves.append(mv)

        return random.choice(best_moves) if best_moves else None

    # -----------------------------------------------------
    # MINIMAX
    # -----------------------------------------------------
    def _evaluate(self, gs):
        return advanced_eval(gs, self.color) if self.use_advanced else basic_eval(gs, self.color)

    def _minimax(self, gs, depth, alpha, beta, maximizing):
        # depth end
        if depth == 0:
            return self._evaluate(gs)

        color_to_move = gs.turn
        moves = self._generate_all_moves(gs, color_to_move)

        if not moves:
            # terminal
            return -10**6 if color_to_move == self.color else 10**6

        if maximizing:
            value = -10**9
            for mv in moves:
                clone = self._clone_game_state(gs)
                try:
                    clone.move(mv[0], mv[1])
                except:
                    continue

                value = max(value, self._minimax(clone, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = 10**9
            for mv in moves:
                clone = self._clone_game_state(gs)
                try:
                    clone.move(mv[0], mv[1])
                except:
                    continue

                value = min(value, self._minimax(clone, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    # -----------------------------------------------------
    # GEN MOVES
    # -----------------------------------------------------
    def _generate_all_moves(self, gs, color):
        moves = []

        for r in range(8):
            for c in range(8):
                p = gs.get_piece(r, c)
                if not p or p.color != color:
                    continue

                board = gs.to_chessboard(sr=r, sc=c)
                board.turn = chess.WHITE if color == 'w' else chess.BLACK

                for m in board.legal_moves:
                    fr = 7 - (m.from_square // 8)
                    fc = m.from_square % 8
                    tr = 7 - (m.to_square // 8)
                    tc = m.to_square % 8

                    if fr == r and fc == c:
                        start_sq = f"{chr(fc + ord('a'))}{8 - fr}"
                        end_sq   = f"{chr(tc + ord('a'))}{8 - tr}"
                        moves.append((start_sq, end_sq))

        return moves

    # -----------------------------------------------------
    # CLONE
    # -----------------------------------------------------
    def _clone_game_state(self, gs):
        from game.game_state import GameState
        from game.conceal import Piece

        clone = GameState.__new__(GameState)
        clone.board = [[None for _ in range(8)] for _ in range(8)]
        clone.turn = gs.turn

        for r in range(8):
            for c in range(8):
                p = gs.get_piece(r, c)
                if p:
                    newp = Piece(
                        true_type=p.true_type,
                        start_type=p.start_type,
                        color=p.color,
                        isKing=p.isKing
                    )
                    newp.isFaceDown = p.isFaceDown
                    clone.board[r][c] = newp

        return clone
