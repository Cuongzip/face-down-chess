from .conceal import Piece
from .board_converter import BoardConverter
import random
import chess
from .random_setup import spawn_random_chinese_style

class GameState:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = 'w'
        spawn_random_chinese_style(self.board)

    # def spawn_random_chinese_style(self):
    #     back_rank = ['R','N','B','Q','K','B','N','R']
    #     pool = ['R','R','N','N','B','B','Q'] + ['P']*8

    #     # WHITE
    #     pool_w = pool.copy()
    #     random.shuffle(pool_w)
    #     idx = 0
    #     for c in range(8):
    #         start_type = back_rank[c]
    #         if start_type == 'K':
    #             true_type = 'K'
    #             isKing = True
    #         else:
    #             true_type = pool_w[idx]; idx += 1
    #             isKing = False
    #         self.board[7][c] = Piece(true_type=true_type, start_type=start_type, color='w', isKing=isKing)

    #     for c in range(8):
    #         if idx < len(pool_w):
    #             true_type = pool_w[idx]; idx += 1
    #         else:
    #             true_type = 'P'
    #         self.board[6][c] = Piece(true_type=true_type, start_type='P', color='w')

    #     # BLACK
    #     pool_b = pool.copy()
    #     random.shuffle(pool_b)
    #     idx = 0
    #     for c in range(8):
    #         start_type = back_rank[c]
    #         if start_type == 'K':
    #             true_type = 'K'
    #             isKing = True
    #         else:
    #             true_type = pool_b[idx]; idx += 1
    #             isKing = False
    #         self.board[0][c] = Piece(true_type=true_type, start_type=start_type, color='b', isKing=isKing)

    #     for c in range(8):
    #         if idx < len(pool_b):
    #             true_type = pool_b[idx]; idx += 1
    #         else:
    #             true_type = 'P'
    #         self.board[1][c] = Piece(true_type=true_type, start_type='P', color='b')

    def get_piece(self, r, c):
        return self.board[r][c]

    def debug_click_log(self, r, c):
        p = self.get_piece(r,c)
        if not p:
            return f"CLICK {r} {c} | EMPTY | turn={self.turn}"
        return (f"CLICK {r} {c} | FD={p.isFaceDown} | start={p.start_type} | true={p.true_type} "
                f"| color={p.color} | turn={self.turn}")

    def to_chessboard(self, sr=None, sc=None):
        return BoardConverter.board_to_chessboard(self.board, self.turn, sr=sr, sc=sc)

    def move(self, start_square, end_square):
        sc = ord(start_square[0]) - ord('a')
        sr = 8 - int(start_square[1])
        ec = ord(end_square[0]) - ord('a')
        er = 8 - int(end_square[1])

        piece = self.get_piece(sr, sc)
        if piece is None:
            raise ValueError("No piece at start")

        if piece.color != self.turn:
            raise ValueError(f"Not {piece.color}'s turn")

        board = self.to_chessboard(sr=sr, sc=sc)

        target_moves = []
        for m in board.legal_moves:
            if m.from_square == chess.square(sc, 7 - sr) and \
               m.to_square == chess.square(ec, 7 - er):
                target_moves.append(m)

        if not target_moves:
            raise ValueError("Illegal move")

        dest = self.get_piece(er, ec)
        captured = dest if dest else None

        BoardConverter.update_board_from_move(self.board, sr, sc, er, ec)

        flipped = False
        if piece.isFaceDown and not piece.isKing:
            piece.flip()
            flipped = True

        # change turn
        self.turn = 'b' if self.turn == 'w' else 'w'

        return {
            "moved": (sr, sc, er, ec),
            "captured": captured,
            "flipped": flipped,
            "turn": self.turn
        }

    # ===========================
    # Support for MinimaxAI clone
    # ===========================
    def clone(self):
        """Safer clone nếu bạn muốn gọi trực tiếp."""
        from .conceal import Piece
        new = GameState.__new__(GameState)
        new.board = [[None for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    np = Piece(true_type=p.true_type, start_type=p.start_type,
                               color=p.color, isKing=p.isKing)
                    np.isFaceDown = p.isFaceDown
                    new.board[r][c] = np
        new.turn = self.turn
        return new
