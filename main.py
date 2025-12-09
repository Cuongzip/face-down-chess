import pygame
import sys
import threading
import time
from game.game_state import GameState
from ai.minimax_ai import MinimaxAI
from ai.difficulty import Difficulty

pygame.init()

MARGIN = 30

SIZE = 80
BOARD_SIZE = SIZE * 8
PLAYER_SIZE = 45

SIDEBAR_W = 350
SIDEBAR_H = BOARD_SIZE + PLAYER_SIZE * 2
SIDEBAR_X = BOARD_SIZE + MARGIN * 2


WINDOW_H = BOARD_SIZE + 2 * MARGIN + PLAYER_SIZE * 2
WINDOW_W = BOARD_SIZE + 3 * MARGIN + SIDEBAR_W

FPS = 30


BG = (15, 28, 48)

LIGHT = (245, 245, 200)
DARK = (180, 120, 80)
CIRCLE = (100, 100, 100)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0, 120)


screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Player vs AI Chess")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Roboto", 28, bold=True)

# ================= GAME STATE =================
state = GameState()
# thử MEDIUM để nhanh hơn
ai = MinimaxAI(color='b', difficulty=Difficulty.MEDIUM)

selected = None
legal_moves = []

no_capture_counter = 0
MAX_NO_CAPTURE = 30

ai_thinking = False
ai_move_ready = None


DIFFICULTY_LABELS = ["Dễ", "Trung bình", "Khó"]


def draw_piece(r, c, p):
    x = MARGIN + c * SIZE
    y = MARGIN + r * SIZE + PLAYER_SIZE
    if p.isFaceDown:
        pygame.draw.circle(screen, CIRCLE, (x + SIZE//2, y + SIZE//2), SIZE//3)
    else:
        txt_color = TEXT_WHITE if p.color == 'w' else TEXT_BLACK
        img = font.render(p.true_type, True, txt_color)
        screen.blit(img, (x + SIZE//2 - img.get_width() //
                    2, y + SIZE//2 - img.get_height()//2))


def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (MARGIN + c*SIZE,
                             MARGIN + r*SIZE + PLAYER_SIZE, SIZE, SIZE))

            # highlight legal moves
            if (r, c) in legal_moves:
                s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                screen.blit(
                    s, (MARGIN + c*SIZE, MARGIN + r*SIZE + PLAYER_SIZE))

            p = state.get_piece(r, c)
            if p:
                draw_piece(r, c, p)


def draw_sidebar():

    RADIUS = 3
    wrapper_rect = pygame.Rect(
        SIDEBAR_X, MARGIN, SIDEBAR_W, SIDEBAR_H)
    pygame.draw.rect(screen, LIGHT, wrapper_rect,
                     width=0, border_radius=RADIUS)

    header_rect = pygame.Rect(
        SIDEBAR_X, MARGIN, SIDEBAR_W, 50)

    pygame.draw.rect(screen, DARK, header_rect, border_top_left_radius=RADIUS,
                     border_top_right_radius=RADIUS)

    icon_text = font.render("Play Bots", True, TEXT_WHITE)
    icon_text_rect = icon_text.get_rect(center=header_rect.center)
    screen.blit(icon_text, icon_text_rect)

    for i, label in enumerate(DIFFICULTY_LABELS):
        button_rect = pygame.Rect(
            SIDEBAR_X + 20, (i + 2) * MARGIN + header_rect.height + i * 50, SIDEBAR_W - 40, 50)
        pygame.draw.rect(screen, DARK, button_rect, border_radius=RADIUS)

        text = font.render(label, True, TEXT_WHITE)
        text_rect = text.get_rect(center=button_rect.center)

        screen.blit(text, text_rect)

    button_rect = pygame.Rect(
        SIDEBAR_X + 10, SIDEBAR_H + MARGIN - 70, SIDEBAR_W - 20, 60)
    pygame.draw.rect(screen, DARK, button_rect, border_radius=RADIUS)

    text = font.render("Chơi", True, TEXT_WHITE)
    text_rect = text.get_rect(center=button_rect.center)

    screen.blit(text, text_rect)

    PLAY_SIDES = ["white_side_icon", "black_side_icon", "random_side_icon"]

    for i, image in enumerate(DIFFICULTY_LABELS):
        pygame.draw.rect(screen, TEXT_WHITE, (SIDEBAR_X + SIDEBAR_W -
                         ((i + 1) * 20 + 10 + i * 5), SIDEBAR_H + MARGIN - 100, 20, 20))


def screen_to_board(mx, my):
    if mx < MARGIN or my < MARGIN:
        return None
    c = (mx - MARGIN) // SIZE
    r = (my - MARGIN - PLAYER_SIZE) // SIZE
    if 0 <= r < 8 and 0 <= c < 8:
        return r, c
    return None


def compute_legal_moves_for(r, c):
    p = state.get_piece(r, c)
    if not p:
        return []
    board = state.to_chessboard(sr=r, sc=c)
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
    global selected_difficulty_idx, human_color, ai, state, no_capture_counter, ai_thinking

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
            elif ev.type == pygame.MOUSEBUTTONDOWN:

                # --- existing board click handling (only when human turn) ---
                if state.turn == 'w':
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
        draw_sidebar()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_loop()
