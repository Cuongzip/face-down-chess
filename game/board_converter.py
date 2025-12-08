import chess

class BoardConverter:
    piece_map = {
        'P': chess.PAWN,
        'N': chess.KNIGHT,
        'B': chess.BISHOP,
        'R': chess.ROOK,
        'Q': chess.QUEEN,
        'K': chess.KING
    }

    @staticmethod
    def board_to_chessboard(board, turn, sr=None, sc=None):
        b = chess.Board(None)

        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p is None:
                    continue

                if sr is not None and sc is not None and r == sr and c == sc and p.isFaceDown and not p.isKing:
                    p_type = p.start_type
                else:
                    p_type = p.true_type

                if p_type not in BoardConverter.piece_map:
                    continue

                piece = chess.Piece(
                    BoardConverter.piece_map[p_type],
                    chess.WHITE if p.color == 'w' else chess.BLACK
                )
                sq = chess.square(c, 7 - r)
                b.set_piece_at(sq, piece)

        b.turn = chess.WHITE if turn == 'w' else chess.BLACK
        b.castling_rights = 0
        return b

    @staticmethod
    def update_board_from_move(board, sr, sc, er, ec):
        piece = board[sr][sc]
        board[er][ec] = piece
        board[sr][sc] = None
