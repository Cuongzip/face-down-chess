import pygame
import sys
import threading
import random
import os
import chess
from game.game_state import GameState
from ai.minimax_ai import MinimaxAI
from ai.difficulty import Difficulty
from ui.board import Board
from ui.sidebar import Sidebar
from ui.player_panel import PlayerPanel

from constants import WINDOW_W, WINDOW_H, BG, FPS
from constants import TEXT_WHITE

pygame.init()


screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Player vs AI Chess")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Roboto", 28, bold=True)

# ================= GAME STATE =================
state = GameState()
human_color = 'w'
ai_color = 'b'
ai = MinimaxAI(color=ai_color, difficulty=Difficulty.MEDIUM)

selected = None
legal_moves = []
last_move = None

no_capture_counter = 0
MAX_NO_CAPTURE = 30

ai_thinking = False
ai_move_ready = None
history = []  # lưu (clone_state, no_capture_counter, mover_color) để undo

# ================= LOAD ASSETS =================
UI_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "ui", "assets")
UI_PIECE_DIR = os.path.join(UI_ASSETS_DIR, "piece")


background_img = None
background_path = os.path.join(UI_ASSETS_DIR, "background.png")
if os.path.isfile(background_path):
    try:
        background_img = pygame.image.load(background_path).convert()
    except Exception as e:
        print(f"[LOAD-ERR] Failed to load background image: {e}")
else:
    # Try alternative formats
    for ext in [".png", ".jpg", ".jpeg"]:
        alt_path = background_path.replace(".png", ext)
        if os.path.isfile(alt_path):
            try:
                background_img = pygame.image.load(alt_path).convert()
                break
            except Exception as e:
                continue
    if background_img is None:
        print(f"[LOAD-ERR] Background file not found: {background_path}")

# Load board image (stone.png)
board_img = None
stone_path = os.path.join(UI_ASSETS_DIR, "stone.png")
if os.path.isfile(stone_path):
    try:
        board_img = pygame.image.load(stone_path).convert_alpha()
    except Exception as e:
        print(f"[LOAD-ERR] Failed to load board image: {e}")

# Load piece images (wk.png, wp.png, bk.png, bp.png, etc.)
piece_images = {}
piece_types = {"k": "King", "q": "Queen", "r": "Rook",
               "b": "Bishop", "n": "Knight", "p": "Pawn"}
for color in ["w", "b"]:
    for piece_char in ["k", "q", "r", "b", "n", "p"]:
        filename = f"{color}{piece_char}.png"
        filepath = os.path.join(UI_PIECE_DIR, filename)
        if os.path.isfile(filepath):
            try:
                piece_images[f"{color}{piece_char}"] = pygame.image.load(
                    filepath).convert_alpha()
            except Exception as e:
                print(f"[LOAD-ERR] Failed to load {filename}: {e}")


# Load user avatar
user_avatar = None
user_avatar_path = os.path.join(UI_ASSETS_DIR, "user-avatar.png")
if os.path.isfile(user_avatar_path):
    try:
        user_avatar = pygame.image.load(user_avatar_path).convert_alpha()
    except Exception as e:
        print(f"[LOAD-ERR] Failed to load user avatar: {e}")

# Load difficulty icons for bot avatar
difficulty_icons = {}
icon_files = {
    0: "easy-level-icon.png",
    1: "medium-level-icon.png",
    2: "hard-level-icon.png"
}
for idx, filename in icon_files.items():
    icon_path = os.path.join(UI_ASSETS_DIR, filename)
    if os.path.isfile(icon_path):
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            difficulty_icons[idx] = icon
        except Exception as e:
            print(f"[LOAD-ERR] Failed to load {filename}: {e}")
            difficulty_icons[idx] = None
    else:
        difficulty_icons[idx] = None


# ================= AI THREAD =================


def ai_compute_move():
    global ai_thinking, ai_move_ready
    if ai_thinking:
        return
    ai_thinking = True

    def compute():
        global ai_thinking, ai_move_ready, ai, state
        mv = ai.choose_move(state)
        ai_move_ready = mv
        ai_thinking = False

    threading.Thread(target=compute, daemon=True).start()


# ================= HELPERS =================


def difficulty_from_index(idx: int) -> Difficulty:
    if idx == 0:
        return Difficulty.EASY
    if idx == 2:
        return Difficulty.HARD
    return Difficulty.MEDIUM


def reset_game(sidebar, selected_play_side):
    """
    Reset game dùng cấu hình trong sidebar (side + difficulty).
    selected_play_side: 0=white, 1=random, 2=black
    """
    global state, ai, ai_thinking, ai_move_ready, selected, legal_moves, no_capture_counter, human_color, ai_color, history, endgame_shown
    state = GameState()
    ai_thinking = False
    ai_move_ready = None
    selected = None
    legal_moves = []
    no_capture_counter = 0
    history = []
    endgame_shown = False
    last_move = None

    if selected_play_side == 1:
        human_color = random.choice(['w', 'b'])
    elif selected_play_side == 2:
        human_color = 'b'
    else:
        human_color = 'w'

    ai_color = 'b' if human_color == 'w' else 'w'

    ai = MinimaxAI(
        color=ai_color, difficulty=difficulty_from_index(sidebar.difficulty))

    state.turn = 'w'


# ================= MAIN LOOP =================


def main_loop():
    global selected, legal_moves, no_capture_counter, ai_move_ready
    global human_color, ai_color, ai, state, ai_thinking, history, endgame_shown, last_move

    board = Board(board_img=board_img, piece_images=piece_images)
    sidebar = Sidebar()
    players = PlayerPanel(font, user_avatar=user_avatar,
                          bot_icons=difficulty_icons)
    reset_game(sidebar, sidebar.play_side)

    endgame_shown = False

    def on_start():
        global human_color, ai_color
        reset_game(sidebar, sidebar.play_side)
        sidebar.start_game()
    sidebar.set_on_start(on_start)

    def on_new_game():
        global human_color, ai_color, last_move
        sidebar.stop_game()
        reset_game(sidebar, sidebar.play_side)
        last_move = None
    sidebar.set_on_new_game(on_new_game)

    def on_undo():
        global state, ai_thinking, ai_move_ready, selected, legal_moves, no_capture_counter, last_move
        if not history:
            return

        # Tìm nước đi gần nhất của người chơi trong history
        target_idx = None
        for i in range(len(history) - 1, -1, -1):
            if history[i][2] == human_color:
                target_idx = i
                break

        if target_idx is None:
            # Không có nước đi nào của người chơi trong history
            return

        # Lấy snapshot TRƯỚC nước đi của người chơi (để restore về đây)
        restore_state, restore_no_cap, _ = history[target_idx]

        # Xóa tất cả các entry từ cuối đến target_idx (bao gồm cả nước của AI sau đó)
        for j in range(len(history) - 1, target_idx - 1, -1):
            _, _, mover = history.pop()
            sidebar.undo_move(mover)

        state = restore_state.clone()
        no_capture_counter = restore_no_cap

        # Reset FLAGS để AI không bị chạy dở
        ai_thinking = False
        ai_move_ready = None
        selected = None
        legal_moves = []
        last_move = None
    sidebar.set_on_undo(on_undo)
    running = True
    while running:
        if sidebar.started and not endgame_shown:
            chess_board = state.to_chessboard()

            def show_overlay(title, subtitle=None, timeout_ms=3000):
                # Clear last move highlight
                last_move = None

                overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                title_font = pygame.font.SysFont("Roboto", 48, bold=True)
                sub_font = pygame.font.SysFont("Roboto", 26, bold=False)

                title_surf = title_font.render(title, True, TEXT_WHITE)
                title_rect = title_surf.get_rect(
                    center=(WINDOW_W // 2, WINDOW_H // 2 - 20))
                overlay.blit(title_surf, title_rect)

                if subtitle:
                    sub_surf = sub_font.render(subtitle, True, TEXT_WHITE)
                    sub_rect = sub_surf.get_rect(
                        center=(WINDOW_W // 2, WINDOW_H // 2 + 30))
                    overlay.blit(sub_surf, sub_rect)

                start = pygame.time.get_ticks()
                waiting = True
                while waiting:
                    # Vẽ lại màn hình mỗi frame để overlay luôn hiển thị
                    if background_img:
                        scaled_bg = pygame.transform.smoothscale(
                            background_img, (WINDOW_W, WINDOW_H))
                        screen.blit(scaled_bg, (0, 0))
                    else:
                        screen.fill(BG)

                    # Vẽ game state (đã dừng)
                    players.draw(screen, sidebar)
                    board.draw(screen, state, legal_moves,
                               flipped=(human_color == 'b'), last_move=last_move)
                    sidebar.draw(screen)

                    # Vẽ overlay lên trên
                    screen.blit(overlay, (0, 0))
                    pygame.display.flip()

                    events = pygame.event.get()
                    for ev in events:
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        # Tắt overlay khi click hoặc nhấn phím
                        if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                            waiting = False
                            break

                    if pygame.time.get_ticks() - start >= timeout_ms:
                        waiting = False

                    clock.tick(FPS)

                # Sau khi tắt overlay, vẽ lại màn hình không có overlay
                if background_img:
                    scaled_bg = pygame.transform.smoothscale(
                        background_img, (WINDOW_W, WINDOW_H))
                    screen.blit(scaled_bg, (0, 0))
                else:
                    screen.fill(BG)

                players.draw(screen, sidebar)
                board.draw(screen, state, legal_moves,
                           flipped=(human_color == 'b'), last_move=None)
                sidebar.draw(screen)
                pygame.display.flip()

            try:

                is_check = chess_board.is_check()
                chess_legal_moves = list(chess_board.legal_moves)
                chess_legal_moves_count = len(chess_legal_moves)

                if is_check and chess_legal_moves_count == 0 and chess_board.is_checkmate():

                    loser_is_white = (chess_board.turn == chess.WHITE)
                    winner_color = 'b' if loser_is_white else 'w'
                    winner_label = "Trắng" if winner_color == 'w' else "Đen"
                    msg = "Bạn thắng!" if human_color == winner_color else "Bạn thua!"
                    print(
                        f"[CHECKMATE] {winner_label} thắng - is_check={is_check}, legal_moves={chess_legal_moves_count}")
                    show_overlay(f"{winner_label} thắng", msg)
                    endgame_shown = True
                    continue
                elif is_check and chess_legal_moves_count > 0:
                    # Có check nhưng không phải checkmate (có legal moves)
                    pass

                # Stalemate: không có check NHƯNG không có legal moves
                if not is_check and chess_legal_moves_count == 0:
                    if chess_board.is_stalemate():
                        print(
                            f"[STALEMATE] Stalemate - is_check={is_check}, legal_moves={chess_legal_moves_count}")
                        show_overlay("Hòa", "Stalemate")
                        endgame_shown = True
                        continue

                if chess_board.is_insufficient_material():
                    print(f"[DRAW] Insufficient material")
                    show_overlay("Hòa", "Insufficient material")
                    endgame_shown = True
                    continue
            except Exception as e:
                print(f"[ENDGAME] chess check failed: {e}")
                import traceback
                traceback.print_exc()

            w_king, b_king = state.has_kings()
            if not w_king or not b_king:
                print(
                    f"[ENDGAME] Kings present? w_king={w_king} b_king={b_king}")
                if not w_king and not b_king:
                    show_overlay("Hòa", "Cả hai bên mất vua")
                elif not w_king:
                    winner = "Đen"
                    msg = "Bạn thắng!" if human_color == 'b' else "Bạn thua!"
                    show_overlay(f"{winner} thắng", msg)
                else:
                    winner = "Trắng"
                    msg = "Bạn thắng!" if human_color == 'w' else "Bạn thua!"
                    show_overlay(f"{winner} thắng", msg)
                endgame_shown = True
                continue

            if no_capture_counter >= MAX_NO_CAPTURE:
                show_overlay("Hòa", "30 nước không ăn")
                endgame_shown = True
                continue

        if sidebar.started and state.turn == ai_color:
            if ai_move_ready is None:
                ai_compute_move()
            else:
                mv = ai_move_ready
                if mv:
                    try:
                        history.append(
                            (state.clone(), no_capture_counter, ai_color))
                        res = state.move(mv[0], mv[1])
                        no_capture_counter = 0 if res["captured"] else no_capture_counter + 1
                        sidebar.add_move(ai_color, f"{mv[0]} {mv[1]}")
                        # Set last move
                        sc, sr = ord(mv[0][0]) - ord('a'), 8 - int(mv[0][1])
                        ec, er = ord(mv[1][0]) - ord('a'), 8 - int(mv[1][1])
                        last_move = (sr, sc, er, ec)
                    except Exception as e:
                        print("AI Move error:", e)
                ai_move_ready = None

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            is_sidebar_click = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                from constants import SIDEBAR_X, SIDEBAR_W
                if SIDEBAR_X <= mx <= SIDEBAR_X + SIDEBAR_W:
                    is_sidebar_click = True

            sidebar.handle_event(ev)

            if sidebar.started and not is_sidebar_click:
                saved_state = None
                saved_counter = None
                if (state.turn == human_color and
                    ev.type == pygame.MOUSEBUTTONDOWN and
                    ev.button == 1 and
                        selected is not None):
                    saved_state = state.clone()
                    saved_counter = no_capture_counter

                selected, legal_moves, move_result = board.handle_event(
                    ev, state, selected, legal_moves, human_color=human_color, flipped=(human_color == 'b'))

                if move_result:
                    if saved_state is not None:
                        history.append(
                            (saved_state, saved_counter, human_color))
                    if move_result["captured"]:
                        no_capture_counter = 0
                    else:
                        no_capture_counter += 1
                    sidebar.add_move(
                        human_color, f"{move_result.get('start_sq', '')} {move_result.get('end_sq', '')}")
                    last_move = move_result["moved"]

        if background_img:
            scaled_bg = pygame.transform.smoothscale(
                background_img, (WINDOW_W, WINDOW_H))
            screen.blit(scaled_bg, (0, 0))
        else:
            screen.fill(BG)

        players.draw(screen, sidebar)
        board.draw(screen, state, legal_moves, flipped=(
            human_color == 'b'), last_move=last_move)
        sidebar.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_loop()
