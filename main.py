import pygame
import sys
import threading
import random
import os
from game.game_state import GameState
from ai.minimax_ai import MinimaxAI
from ai.difficulty import Difficulty
from ui.board import Board
from ui.sidebar import Sidebar
from ui.player_panel import PlayerPanel

from constants import WINDOW_W, WINDOW_H, MARGIN, PLAYER_SIZE, SIZE, BG, FPS
from constants import BOARD_SIZE, TEXT_WHITE

pygame.init()


screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Player vs AI Chess")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Roboto", 28, bold=True)

# ================= GAME STATE =================
state = GameState()
# mặc định human chơi trắng, AI chơi đen
human_color = 'w'
ai_color = 'b'
ai = MinimaxAI(color=ai_color, difficulty=Difficulty.MEDIUM)

selected = None
legal_moves = []

no_capture_counter = 0
MAX_NO_CAPTURE = 30

ai_thinking = False
ai_move_ready = None
history = []  # lưu (clone_state, no_capture_counter, mover_color) để undo

# ================= LOAD ASSETS =================
UI_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "ui", "assets")
UI_PIECE_DIR = os.path.join(UI_ASSETS_DIR, "piece")

# Load board image (stone.png)
board_img = None
stone_path = os.path.join(UI_ASSETS_DIR, "stone.png")
if os.path.isfile(stone_path):
    try:
        board_img = pygame.image.load(stone_path).convert_alpha()
        print(f"[LOAD] Loaded board image: {stone_path}")
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
                print(f"[LOAD] Loaded piece: {filename}")
            except Exception as e:
                print(f"[LOAD-ERR] Failed to load {filename}: {e}")

print(f"[REPORT] Loaded {len(piece_images)}/12 piece images")


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
    global state, ai, ai_thinking, ai_move_ready, selected, legal_moves, no_capture_counter, human_color, ai_color, history
    state = GameState()
    ai_thinking = False
    ai_move_ready = None
    selected = None
    legal_moves = []
    no_capture_counter = 0
    history = []

    # map play_side: 0 = white, 1 = random, 2 = black
    if selected_play_side == 1:  # random
        human_color = random.choice(['w', 'b'])
    elif selected_play_side == 2:  # black
        human_color = 'b'
    else:  # 0 = white
        human_color = 'w'

    ai_color = 'b' if human_color == 'w' else 'w'

    ai = MinimaxAI(
        color=ai_color, difficulty=difficulty_from_index(sidebar.difficulty))

    # Luôn bắt đầu với trắng đi trước; nếu human chơi đen thì AI (trắng) sẽ đi trước
    state.turn = 'w'

    print(
        f"[RESET] human_color={human_color}, ai_color={ai_color}, play_side={selected_play_side}")


# ================= MAIN LOOP =================


def main_loop():
    global selected, legal_moves, no_capture_counter, ai_move_ready
    global human_color, ai_color, ai, state, ai_thinking, history

    board = Board(board_img=board_img, piece_images=piece_images)
    sidebar = Sidebar()
    players = PlayerPanel(font)
    # chưa bắt đầu game cho đến khi bấm "Chơi"
    reset_game(sidebar, sidebar.play_side)

    # gán callback để chỉ bắt đầu/reset khi bấm "Chơi"
    def on_start():
        global human_color, ai_color  # ensure global sync
        reset_game(sidebar, sidebar.play_side)
        print(
            f"[on_start] after reset: human_color={human_color}, play_side={sidebar.play_side}")
        sidebar.start_game()
    sidebar.set_on_start(on_start)
    # "Ván mới": quay về màn chọn (stop_game) rồi chuẩn bị state sẵn (chưa start)

    def on_new_game():
        global human_color, ai_color  # ensure global sync
        sidebar.stop_game()
        reset_game(sidebar, sidebar.play_side)
        print(
            f"[on_new_game] after reset: human_color={human_color}, play_side={sidebar.play_side}")
    sidebar.set_on_new_game(on_new_game)

    def on_undo():
        global state, ai_thinking, ai_move_ready, selected, legal_moves, no_capture_counter
        if not history:
            return

        # Find the last snapshot that belongs to the human player
        target_idx = None
        for i in range(len(history) - 1, -1, -1):
            if history[i][2] == human_color:
                target_idx = i
                break

        if target_idx is None:
            # no human move in history — nothing to undo
            return

        # Save snapshot to restore (snapshot before the human's move)
        restore_state, restore_no_cap, _ = history[target_idx]

        # Pop and undo move_log entries from the end down to target_idx (inclusive)
        for j in range(len(history) - 1, target_idx - 1, -1):
            _, _, mover = history.pop()
            sidebar.undo_move(mover)

        # Restore the saved snapshot
        state = restore_state
        no_capture_counter = restore_no_cap

        # Reset FLAGS để AI không bị chạy dở
        ai_thinking = False
        ai_move_ready = None
        selected = None
        legal_moves = []
    sidebar.set_on_undo(on_undo)
    running = True
    while running:

        # ===== CHECK ENDGAME =====
        chess_board = state.to_chessboard()

        def show_overlay(title, subtitle=None, timeout_ms=2500):
            print(f"[ENDGAME] show_overlay called: {title} - {subtitle}")
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

            # Draw overlay once and then wait for either input or timeout
            screen.blit(overlay, (0, 0))
            pygame.display.flip()

            start = pygame.time.get_ticks()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        waiting = False
                # auto-dismiss after timeout to avoid freezing
                if pygame.time.get_ticks() - start >= timeout_ms:
                    waiting = False
                clock.tick(FPS)

        # Use python-chess to detect checkmate/stalemate/insufficient material
        try:
            if chess_board.is_checkmate():
                loser_is_white = bool(chess_board.turn)
                winner_color = 'b' if loser_is_white else 'w'
                winner_label = "Trắng" if winner_color == 'w' else "Đen"
                msg = "Bạn thắng!" if human_color == winner_color else "Bạn thua!"
                show_overlay(f"{winner_label} thắng", msg)
                break

            if chess_board.is_stalemate():
                show_overlay("Hòa", "Stalemate")
                break

            if chess_board.is_insufficient_material():
                show_overlay("Hòa", "Insufficient material")
                break
        except Exception as e:
            print(f"[ENDGAME] chess check failed: {e}")

        # fallback: king capture detection
        w_king, b_king = state.has_kings()
        if not w_king or not b_king:
            print(f"[ENDGAME] Kings present? w_king={w_king} b_king={b_king}")
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
            break

        if no_capture_counter >= MAX_NO_CAPTURE:
            show_overlay("Hòa", "30 nước không ăn")
            break

        # ===== AI MOVE =====
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
                    except Exception as e:
                        print("AI Move error:", e)
                ai_move_ready = None

        # ===== EVENTS =====
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            if sidebar.started:
                selected, legal_moves, move_result = board.handle_event(
                    ev, state, selected, legal_moves, human_color=human_color, flipped=(human_color == 'b'))
                if move_result:
                    history.append(
                        (state.clone(), no_capture_counter, human_color))
                    if move_result["captured"]:
                        no_capture_counter = 0
                    else:
                        no_capture_counter += 1
                    sidebar.add_move(
                        human_color, f"{move_result.get('start_sq', '')} {move_result.get('end_sq', '')}")
            sidebar.handle_event(ev)

        screen.fill(BG)
        players.draw(screen, sidebar)
        # debug
        print(
            f"[draw] human_color={human_color}, flipped={(human_color == 'b')}")
        board.draw(screen, state, legal_moves, flipped=(human_color == 'b'))
        sidebar.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_loop()
