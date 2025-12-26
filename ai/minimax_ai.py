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

        moves = self._order_moves(gs, moves)

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

        # Sắp xếp moves để alpha-beta hiệu quả hơn
        moves = self._order_moves(gs, moves)

        if maximizing:
            value = -1e9
            for mv in moves:
                clone = gs.clone()
                try:
                    clone.move(mv[0], mv[1])
                except ValueError:
                    continue
                value = max(value, self._minimax(
                    clone, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            return value
        else:
            value = 1e9
            for mv in moves:
                clone = gs.clone()
                try:
                    clone.move(mv[0], mv[1])
                except ValueError:
                    continue
                value = min(value, self._minimax(
                    clone, depth-1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
            return value

    def _evaluate(self, gs: GameState):
        h = tuple((p.true_type, p.color, p.isFaceDown)
                  if p else None for row in gs.board for p in row)
        if h in self._eval_cache:
            return self._eval_cache[h]

        score = advanced_eval(
            gs, self.color) if self.use_advanced else basic_eval(gs, self.color)
        self._eval_cache[h] = score
        return score

    def _order_moves(self, gs: GameState, moves):
        if not moves:
            return moves

        def move_priority(mv):
            try:
                start_sq, end_sq = mv
                sc, sr = ord(start_sq[0]) - ord('a'), 8 - int(start_sq[1])
                ec, er = ord(end_sq[0]) - ord('a'), 8 - int(end_sq[1])

                # Ưu tiên capture moves
                captured = gs.get_piece(er, ec)
                if captured:
                    # Capture có giá trị cao hơn
                    piece_type = captured.true_type[0].lower(
                    ) if captured.true_type else 'p'
                    piece_value = {'p': 1, 'n': 3, 'b': 3,
                                   'r': 5, 'q': 9, 'k': 0}.get(piece_type, 0)
                    return 1000 + piece_value  # Capture moves đi trước

                # Ưu tiên moves ở center
                center_bonus = 0
                if 3 <= er <= 4 and 3 <= ec <= 4:
                    center_bonus = 10

                return center_bonus
            except (ValueError, IndexError, AttributeError):
                return 0  # Nếu có lỗi, đặt priority thấp

        # Sắp xếp theo priority (cao -> thấp)
        moves_with_priority = [(move_priority(mv), mv) for mv in moves]
        moves_with_priority.sort(reverse=True, key=lambda x: x[0])
        return [mv for _, mv in moves_with_priority]

    def _generate_all_moves(self, gs: GameState, color):
        moves = []

        for r in range(8):
            for c in range(8):
                piece = gs.get_piece(r, c)
                if piece and piece.color == color:
                    # tạo board riêng cho quân này để face-down dùng start_type
                    board = gs.to_chessboard(sr=r, sc=c)
                    board.turn = chess.WHITE if color == 'w' else chess.BLACK
                    for m in board.legal_moves:
                        fr, fc = 7 - (m.from_square // 8), m.from_square % 8
                        tr, tc = 7 - (m.to_square // 8), m.to_square % 8
                        if (fr, fc) == (r, c):
                            start_sq = f"{chr(fc + ord('a'))}{8 - fr}"
                            end_sq = f"{chr(tc + ord('a'))}{8 - tr}"
                            moves.append((start_sq, end_sq))
        return moves
