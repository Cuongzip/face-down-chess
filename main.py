import pygame
import sys
from game.game_state import GameState
from ai.difficulty import Difficulty, get_depth
from ai.minimax_ai import MinimaxAI

pygame.init()

SIZE = 60
MARGIN = 30
BOARD_SIZE = SIZE * 8
WINDOW_SIZE = BOARD_SIZE + 2 * MARGIN
FPS = 30

LIGHT = (230,230,230)
DARK = (150,150,150)
BG = (30,30,30)
HIGHLIGHT = (255,0,0,120)

CIRCLE = (210,210,210)
TEXT_WHITE = (20,20,20)
TEXT_BLACK = (240,240,240)

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Face-down Chinese-style Chess (Chess rules) - Test")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28, bold=True)

# GAME STATE
state = GameState()

# AI difficulty
DIFF = Difficulty.EASY

# AI always plays black
ai = MinimaxAI(color='b', difficulty=DIFF)

selected = None
legal_moves = []


# ========================= DRAW ===========================

def draw_piece(r, c, p):
    x = MARGIN + c * SIZE
    y = MARGIN + r * SIZE

    if p.isFaceDown:
        pygame.draw.circle(screen, CIRCLE, (x + SIZE//2, y + SIZE//2), SIZE//3)
    else:
        txt_color = TEXT_WHITE if p.color == 'w' else TEXT_BLACK
        img = font.render(p.true_type, True, txt_color)
        screen.blit(img, (x + SIZE//2 - img.get_width()//2,
                          y + SIZE//2 - img.get_height()//2))


def draw_board():
    for r in range(8):
        for c in range(8):
            x = MARGIN + c * SIZE
            y = MARGIN + r * SIZE

            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (x, y, SIZE, SIZE))

            # highlight legal moves
            if (r, c) in legal_moves:
                s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                screen.blit(s, (x, y))

            p = state.get_piece(r, c)
            if p:
                draw_piece(r, c, p)


# ====================== HELPERS ========================

def screen_to_board(mx, my):
    if mx < MARGIN or my < MARGIN:
        return None
    c = (mx - MARGIN) // SIZE
    r = (my - MARGIN) // SIZE
    if 0 <= r < 8 and 0 <= c < 8:
        return r, c
    return None


def compute_legal_moves_for(r, c):
    p = state.get_piece(r, c)
    if not p:
        return []

    board = state.to_chessboard(sr=r, sc=c)
    import chess
    moves = []

    for m in board.legal_moves:
        fr = 7 - (m.from_square // 8)
        fc = m.from_square % 8
        tr = 7 - (m.to_square // 8)
        tc = m.to_square % 8
        if fr == r and fc == c:
            moves.append((tr, tc))

    return moves


# ======================= MAIN LOOP ============================

def main_loop():
    global selected, legal_moves

    while True:

        # ---------------- AI TURN ----------------
        if state.turn == 'b':
            ai_move = ai.choose_move(state)

            if ai_move:

                # CASE 1: AI returns (start_sq, end_sq)
                if len(ai_move) == 2:
                    start_sq, end_sq = ai_move

                    sr = 8 - int(start_sq[1])
                    sc = ord(start_sq[0]) - ord('a')

                    tr = 8 - int(end_sq[1])
                    tc = ord(end_sq[0]) - ord('a')

                # CASE 2: AI returns (sr, sc, tr, tc)
                else:
                    sr, sc, tr, tc = ai_move
                    start_sq = f"{chr(sc + ord('a'))}{8 - sr}"
                    end_sq = f"{chr(tc + ord('a'))}{8 - tr}"

                before = state.get_piece(sr, sc)
                bd_before = (before.isFaceDown, before.start_type, before.true_type)

                res = state.move(start_sq, end_sq)

                after = state.get_piece(tr, tc)
                bd_after = (after.isFaceDown, after.start_type, after.true_type)

                print(f"[AI MOVE] {start_sq}->{end_sq} | before FD={bd_before[0]} start={bd_before[1]} true={bd_before[2]} | after FD={bd_after[0]} start={bd_after[1]} true={bd_after[2]} | flipped={res['flipped']}")

                pygame.time.delay(300)

        # ---------------- EVENTS ----------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN and state.turn == 'w':
                pos = screen_to_board(*ev.pos)
                if not pos:
                    continue

                r, c = pos
                p = state.get_piece(r, c)

                # SELECT PHASE
                if selected is None:
                    if p and p.color == 'w':
                        selected = (r, c)
                        legal_moves = compute_legal_moves_for(r, c)
                        print(state.debug_click_log(r, c))
                        print("LEGAL_MOVES:", legal_moves)

                # MOVE PHASE
                else:
                    sr, sc = selected

                    # 1) Click lại ô đang chọn → hủy chọn, không đổi turn
                    if (r, c) == (sr, sc):
                        selected = None
                        legal_moves = []
                        continue

                    # 2) Không phải nước đi hợp lệ → hủy chọn, không đổi turn
                    if (r, c) not in legal_moves:
                        selected = None
                        legal_moves = []
                        continue

                    # 3) Di chuyển hợp lệ
                    start_sq = f"{chr(sc + ord('a'))}{8 - sr}"
                    end_sq   = f"{chr(c + ord('a'))}{8 - r}"

                    before = state.get_piece(sr, sc)
                    bd_before = (before.isFaceDown, before.start_type, before.true_type)

                    try:
                        res = state.move(start_sq, end_sq)

                        after = state.get_piece(r, c)
                        bd_after = (after.isFaceDown, after.start_type, after.true_type)

                        print(
                            f"MOVE {start_sq}->{end_sq} "
                            f"| before FD={bd_before[0]} start={bd_before[1]} true={bd_before[2]} "
                            f"| after FD={bd_after[0]} start={bd_after[1]} true={bd_after[2]} "
                            f"| flipped={res['flipped']}"
                        )

                        # CHỈ đổi turn sau một nước đi hợp lệ
                        state.turn = 'b'

                    except Exception as e:
                        print("Move error:", e)

                    selected = None
                    legal_moves = []

        # ---------------- DRAW ----------------
        screen.fill(BG)
        draw_board()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main_loop()
