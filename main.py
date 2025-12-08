import pygame
import sys
import threading
import time
from game.game_state import GameState
from ai.minimax_ai import MinimaxAI
from ai.difficulty import Difficulty

pygame.init()

SIZE = 60
MARGIN = 30
BOARD_SIZE = SIZE * 8
WINDOW_SIZE = BOARD_SIZE + 2 * MARGIN
FPS = 30

LIGHT = (245, 245, 200)
DARK = (180, 120, 80)
CIRCLE = (100, 100, 100)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (0, 0, 0)
BG = (50, 50, 50)
HIGHLIGHT = (0, 255, 0, 120)

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Player vs AI Chess")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28, bold=True)

# ================= GAME STATE =================
state = GameState()
ai = MinimaxAI(color='b', difficulty=Difficulty.MEDIUM)  # thử MEDIUM để nhanh hơn

selected = None
legal_moves = []

no_capture_counter = 0
MAX_NO_CAPTURE = 30

ai_thinking = False
ai_move_ready = None

# ================= DRAW =================
def draw_piece(r, c, p):
    x = MARGIN + c * SIZE
    y = MARGIN + r * SIZE
    if p.isFaceDown:
        pygame.draw.circle(screen, CIRCLE, (x + SIZE//2, y + SIZE//2), SIZE//3)
    else:
        txt_color = TEXT_WHITE if p.color == 'w' else TEXT_BLACK
        img = font.render(p.true_type, True, txt_color)
        screen.blit(img, (x + SIZE//2 - img.get_width()//2, y + SIZE//2 - img.get_height()//2))

def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (MARGIN + c*SIZE, MARGIN + r*SIZE, SIZE, SIZE))

            # highlight legal moves
            if (r, c) in legal_moves:
                s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                screen.blit(s, (MARGIN + c*SIZE, MARGIN + r*SIZE))

            p = state.get_piece(r, c)
            if p:
                draw_piece(r, c, p)

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
        fr, fc = 7 - (m.from_square // 8), m.from_square % 8
        tr, tc = 7 - (m.to_square // 8), m.to_square % 8
        if (fr, fc) == (r, c):
            moves.append((tr, tc))
    return moves

# ================= AI THREAD =================
def ai_compute_move():
    global ai_thinking, ai_move_ready
    if ai_thinking:
        return
    ai_thinking = True

    def compute():
        global ai_thinking, ai_move_ready
        mv = ai.choose_move(state)
        ai_move_ready = mv
        ai_thinking = False

    threading.Thread(target=compute, daemon=True).start()

# ================= MAIN LOOP =================
def main_loop():
    global selected, legal_moves, no_capture_counter, ai_move_ready

    running = True
    while running:

        # ===== CHECK ENDGAME =====
        w_king, b_king = state.has_kings()
        if not w_king or not b_king:
            print("Game over! One king captured.")
            pygame.time.delay(2000)
            break
        if no_capture_counter >= MAX_NO_CAPTURE:
            print("Draw by 30 moves without capture.")
            pygame.time.delay(2000)
            break

        # ===== AI MOVE =====
        if state.turn == 'b':
            if ai_move_ready is None:
                ai_compute_move()
            else:
                mv = ai_move_ready
                if mv:
                    try:
                        res = state.move(mv[0], mv[1])
                        no_capture_counter = 0 if res["captured"] else no_capture_counter + 1
                    except Exception as e:
                        print("AI Move error:", e)
                ai_move_ready = None

        # ===== EVENTS =====
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN and state.turn == 'w':
                pos = screen_to_board(*ev.pos)
                if not pos:
                    continue
                r, c = pos
                p = state.get_piece(r, c)
                if selected is None:
                    if p and p.color == 'w':
                        selected = (r, c)
                        legal_moves = compute_legal_moves_for(r, c)
                else:
                    sr, sc = selected
                    if (r, c) not in legal_moves:
                        selected = None
                        legal_moves = []
                        continue
                    start_sq = f"{chr(sc+ord('a'))}{8-sr}"
                    end_sq = f"{chr(c+ord('a'))}{8-r}"
                    try:
                        res = state.move(start_sq, end_sq)
                        no_capture_counter = 0 if res["captured"] else no_capture_counter + 1
                    except Exception as e:
                        print("Move error:", e)
                    selected = None
                    legal_moves = []

        # ===== DRAW =====
        screen.fill(BG)
        draw_board()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
