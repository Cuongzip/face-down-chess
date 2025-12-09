import random
from .conceal import Piece

def spawn_random_chinese_style(board):
    back_rank = ['R','N','B','Q','K','B','N','R']
    pool = ['R','R','N','N','B','B','Q'] + ['P']*8

    def fill_color(color, main_row, pawn_row):
        pool_c = pool.copy()
        random.shuffle(pool_c)
        idx = 0
        # Hàng chính
        for c in range(8):
            start_type = back_rank[c]
            if start_type == 'K':
                true_type = 'K'
                isKing = True
            else:
                true_type = pool_c[idx]; idx += 1
                isKing = False
            board[main_row][c] = Piece(true_type=true_type, start_type=start_type, color=color, isKing=isKing)
        # Hàng quân phụ (pawns)
        for c in range(8):
            if idx < len(pool_c):
                true_type = pool_c[idx]; idx += 1
            else:
                true_type = 'P'
            board[pawn_row][c] = Piece(true_type=true_type, start_type='P', color=color)

    # WHITE
    fill_color('w', main_row=7, pawn_row=6)
    # BLACK
    fill_color('b', main_row=0, pawn_row=1)
