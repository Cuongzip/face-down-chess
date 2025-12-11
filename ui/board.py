import pygame
from constants import (
    MARGIN,
    SIZE,
    LIGHT,
    DARK,
    PLAYER_SIZE,
    HIGHLIGHT,
    TEXT_WHITE,
    TEXT_BLACK,
    CIRCLE,
    BOARD_SIZE,
)


class Board:
    def __init__(self, board_img=None, piece_images=None):
        """Initialize board with optional images."""
        self.board_img = board_img
        self.piece_images = piece_images or {}
        self.font = pygame.font.SysFont("Roboto", 20, bold=True)
        self._label_font = pygame.font.SysFont("Roboto", 18, bold=False)

    def draw_piece(self, screen, disp_r, disp_c, p):
        x = MARGIN + disp_c * SIZE
        y = MARGIN + disp_r * SIZE + PLAYER_SIZE

        if p.isFaceDown:
            pygame.draw.circle(
                screen, CIRCLE, (x + SIZE//2, y + SIZE//2), SIZE//3)
        else:
            # Try to use piece image first
            piece_key = f"{p.color}{p.true_type[0].lower()}"
            img_sprite = self.piece_images.get(piece_key)

            if img_sprite:
                try:
                    img_s = pygame.transform.smoothscale(
                        img_sprite, (SIZE - 10, SIZE - 10))
                    screen.blit(img_s, (x + 5, y + 5))
                except Exception:
                    # fallback to text if image fails
                    txt_color = TEXT_WHITE if p.color == 'w' else TEXT_BLACK
                    txt = self.font.render(
                        p.true_type[0].upper(), True, txt_color)
                    screen.blit(txt, (x + SIZE//2 - txt.get_width() //
                                2, y + SIZE//2 - txt.get_height()//2))
            else:
                # No image -> use text letter
                txt_color = TEXT_WHITE if p.color == 'w' else TEXT_BLACK
                txt = self.font.render(p.true_type[0].upper(), True, txt_color)
                screen.blit(txt, (x + SIZE//2 - txt.get_width() //
                            2, y + SIZE//2 - txt.get_height()//2))

    def draw(self, screen, state, legal_moves, flipped=False):
        # Draw board background (image or color grid)
        if self.board_img:
            bw, bh = self.board_img.get_width(), self.board_img.get_height()
            # If board image is small (like 2x2 tiles), tile it
            if bw < BOARD_SIZE or bh < BOARD_SIZE:
                if bw % 2 == 0 and bh % 2 == 0:
                    tile_w = bw // 2
                    tile_h = bh // 2
                    for r in range(8):
                        for c in range(8):
                            disp_r = 7 - r if flipped else r
                            disp_c = 7 - c if flipped else c
                            sx = (disp_c % 2) * tile_w
                            sy = (disp_r % 2) * tile_h
                            try:
                                sub = self.board_img.subsurface(
                                    (sx, sy, tile_w, tile_h))
                                sub_s = pygame.transform.smoothscale(
                                    sub, (SIZE, SIZE))
                                screen.blit(
                                    sub_s, (MARGIN + c*SIZE, MARGIN + r*SIZE + PLAYER_SIZE))
                            except Exception:
                                color = LIGHT if (
                                    disp_r + disp_c) % 2 == 0 else DARK
                                pygame.draw.rect(
                                    screen, color, (MARGIN + c*SIZE, MARGIN + r*SIZE + PLAYER_SIZE, SIZE, SIZE))
            else:
                # Large board image -> scale and blit once
                img = pygame.transform.smoothscale(
                    self.board_img, (BOARD_SIZE, BOARD_SIZE))
                screen.blit(img, (MARGIN, MARGIN + PLAYER_SIZE))
        else:
            # No image -> draw color grid (with flip support)
            for r in range(8):
                for c in range(8):
                    disp_r = 7 - r if flipped else r
                    disp_c = 7 - c if flipped else c
                    color = LIGHT if (disp_r + disp_c) % 2 == 0 else DARK
                    pygame.draw.rect(
                        screen,
                        color,
                        (MARGIN + c * SIZE, MARGIN + r *
                         SIZE + PLAYER_SIZE, SIZE, SIZE),
                    )

        # Highlight legal moves (legal_moves are in board coords)
        for br in range(8):
            for bc in range(8):
                if (br, bc) in legal_moves:
                    disp_r = 7 - br if flipped else br
                    disp_c = 7 - bc if flipped else bc
                    s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
                    s.fill(HIGHLIGHT)
                    screen.blit(
                        s, (MARGIN + disp_c * SIZE, MARGIN +
                            disp_r * SIZE + PLAYER_SIZE)
                    )

        # Draw pieces
        for r in range(8):
            for c in range(8):
                disp_r = 7 - r if flipped else r
                disp_c = 7 - c if flipped else c
                # Get piece from actual board position, not flipped position
                p = state.get_piece(r, c)
                if p:
                    self.draw_piece(screen, disp_r, disp_c, p)

        # Draw rank numbers inside left corner of each row's leftmost square
        for sr in range(8):
            disp_r = 7 - sr if flipped else sr
            # leftmost displayed column on screen
            disp_c_for_rank = 7 if flipped else 0
            label = str(8 - disp_r)
            lbl_surf = self._label_font.render(label, True, TEXT_BLACK)
            # choose contrasting color based on square color
            sq_color_is_light = ((disp_r + disp_c_for_rank) % 2 == 0)
            lbl_color = TEXT_BLACK if sq_color_is_light else TEXT_WHITE
            lbl_surf = self._label_font.render(label, True, lbl_color)
            x = MARGIN + (0 if not flipped else 0) * SIZE + 4
            y = MARGIN + sr * SIZE + PLAYER_SIZE + 4
            screen.blit(lbl_surf, (x, y))

        # Draw file letters inside bottom corner of each column's bottom square
        for sc in range(8):
            disp_c = 7 - sc if flipped else sc
            # bottom displayed row on screen
            disp_r_for_file = 7 if not flipped else 0
            lbl = chr(ord('a') + disp_c)
            # choose contrasting color based on square color
            sq_color_is_light = ((disp_r_for_file + disp_c) % 2 == 0)
            lbl_color = TEXT_BLACK if sq_color_is_light else TEXT_WHITE
            lbl_surf = self._label_font.render(lbl, True, lbl_color)
            x = MARGIN + sc * SIZE + SIZE - lbl_surf.get_width() - 4
            y = MARGIN + BOARD_SIZE + PLAYER_SIZE - lbl_surf.get_height() - 4
            screen.blit(lbl_surf, (x, y))

    def screen_to_board(self, mx, my, flipped=False):
        if mx < MARGIN or my < MARGIN:
            return None
        c = (mx - MARGIN) // SIZE
        r = (my - MARGIN - PLAYER_SIZE) // SIZE
        if 0 <= r < 8 and 0 <= c < 8:
            board_r, board_c = (7 - r, 7 - c) if flipped else (r, c)
            return board_r, board_c
        return None

    def compute_legal_moves_for(self, state, r, c):
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

    def handle_event(self, ev, state, selected, legal_moves, human_color='w', flipped=False):
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return selected, legal_moves, None

        if state.turn != human_color:
            return selected, legal_moves, None

        pos = self.screen_to_board(*ev.pos, flipped=flipped)
        if not pos:
            return selected, legal_moves, None

        r, c = pos
        p = state.get_piece(r, c)

        if selected is None:
            if p and p.color == human_color:
                selected = (r, c)
                legal_moves = self.compute_legal_moves_for(state, r, c)
            return selected, legal_moves, None

        if p and p.color == human_color and (r, c) != selected:
            selected = (r, c)
            legal_moves = self.compute_legal_moves_for(state, r, c)
            return selected, legal_moves, None

        sr, sc = selected
        if (r, c) not in legal_moves:
            return None, [], None

        start_sq = f"{chr(sc+ord('a'))}{8-sr}"
        end_sq = f"{chr(c+ord('a'))}{8-r}"

        try:
            result = state.move(start_sq, end_sq)
            result["start_sq"] = start_sq
            result["end_sq"] = end_sq
        except Exception as e:
            print("Move error:", e)
            return None, [], None

        return None, [], result
