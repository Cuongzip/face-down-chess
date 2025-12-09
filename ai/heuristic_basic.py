# ai/basic_heuristic.py

PIECE_VALUES = {
    'P': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 20000
}

def basic_eval(gs, color):
    """
    Basic material evaluation from perspective of 'color' ('w' or 'b').
    Positive = good for color, negative = bad.
    """
    score = 0
    for r in range(8):
        for c in range(8):
            p = gs.get_piece(r, c)
            if not p:
                continue
            val = PIECE_VALUES.get(p.true_type, 0)
            if p.color == color:
                score += val
            else:
                score -= val
    return score
