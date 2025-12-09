from .conceal import Piece
from .board_converter import BoardConverter
from .random_setup import spawn_random_chinese_style
import chess

class GameState:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = 'w'
        spawn_random_chinese_style(self.board)

    def get_piece(self, r, c):
        return self.board[r][c]

    def debug_click_log(self, r, c):
        p = self.get_piece(r, c)
        if not p:
            return f"CLICK {r} {c} | EMPTY | turn={self.turn}"
        return (f"CLICK {r} {c} | FD={p.isFaceDown} | start={p.start_type} "
                f"| true={p.true_type} | color={p.color} | turn={self.turn}")

    def to_chessboard(self, sr=None, sc=None):
        # chuyển GameState.board sang python-chess Board
        return BoardConverter.board_to_chessboard(self.board, self.turn, sr=sr, sc=sc)

    def move(self, start_square, end_square):
        sc, sr = ord(start_square[0]) - ord('a'), 8 - int(start_square[1])
        ec, er = ord(end_square[0]) - ord('a'), 8 - int(end_square[1])

        piece = self.get_piece(sr, sc)
        if piece is None:
            raise ValueError("No piece at start")
        if piece.color != self.turn:
            raise ValueError(f"Not {piece.color}'s turn")

        board = self.to_chessboard(sr=sr, sc=sc)

        target_moves = [m for m in board.legal_moves
                        if m.from_square == chess.square(sc, 7 - sr)
                        and m.to_square == chess.square(ec, 7 - er)]

        if not target_moves:
            raise ValueError("Illegal move")

        captured = self.get_piece(er, ec)
        BoardConverter.update_board_from_move(self.board, sr, sc, er, ec)

        flipped = False
        if piece.isFaceDown and not piece.isKing:
            piece.flip()
            flipped = True

        # đổi turn
        self.turn = 'b' if self.turn == 'w' else 'w'

        return {
            "moved": (sr, sc, er, ec),
            "captured": captured,
            "flipped": flipped,
            "turn": self.turn
        }

    # ===============================
    # Lightweight clone cho AI
    # ===============================
    def clone(self):
        new = GameState.__new__(GameState)
        new.turn = self.turn
        new.board = [[None]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    np = Piece(p.true_type, p.start_type, p.color, p.isKing)
                    np.isFaceDown = p.isFaceDown
                    new.board[r][c] = np
        return new

    # ===============================
    # Kiểm tra vua còn tồn tại
    # ===============================
    def has_kings(self):
        w_king = any(p for row in self.board for p in row if p and p.isKing and p.color == 'w')
        b_king = any(p for row in self.board for p in row if p and p.isKing and p.color == 'b')
        return w_king, b_king
