from game.board_converter import BoardConverter

PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000
}

# Piece-square tables (PST)
PST = {
    'P': [0,0,0,0,0,0,0,0,5,10,10,-20,-20,10,10,5,5,-5,-10,0,0,-10,-5,5,0,0,0,20,20,0,0,0,5,5,10,25,25,10,5,5,10,10,20,30,30,20,10,10,50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0],
    'N': [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
    'B': [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
    'R': [0,0,0,5,5,0,0,0,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,5,10,10,10,10,10,10,5,0,0,0,0,0,0,0,0],
    'Q': [0]*64, 'K': [0]*64,
}


def advanced_eval(gs, color):
    score = 0
    own_mob = 0
    opp_mob = 0
    center_squares = {(3,3),(3,4),(4,3),(4,4)}

    # --- Material + PST ---
    for r in range(8):
        for c in range(8):
            p = gs.get_piece(r, c)
            if not p:
                continue

            base = PIECE_VALUES.get(p.true_type, 0)
            pst = PST.get(p.true_type, [0]*64)
            idx = (7 - r) * 8 + c
            val = base + pst[idx]

            score += val if p.color == color else -val
            if (r, c) in center_squares:
                score += 10 if p.color == color else -10

    # --- Mobility (tối ưu) ---
    chess_board = BoardConverter.board_to_chessboard(gs.board, gs.turn)
    for m in chess_board.legal_moves:
        fr, fc = 7 - (m.from_square // 8), m.from_square % 8
        piece = gs.get_piece(fr, fc)
        if not piece:
            continue
        if piece.color == color:
            own_mob += 1
        else:
            opp_mob += 1
    score += 10 * (own_mob - opp_mob)

    return score
