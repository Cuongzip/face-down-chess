import pygame
import os
from ui.button import Button
from constants import MARGIN, SIDEBAR_X, LIGHT, DARK, SIDEBAR_W, SIDEBAR_H, TEXT_WHITE


class Sidebar:
    def __init__(self):
        self.buttons = []
        self.button_meta = []
        self.difficulty = 1
        self.play_side = 0
        self.human_color = 'w'
        self.on_start = None
        self.on_new_game = None
        self.started = False
        self.move_log = []
        self.scroll_offset = 0
        self.max_lines = 16

        # Load difficulty icons
        UI_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
        self.difficulty_icons = {}
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
                    # Scale icon to appropriate size
                    icon = pygame.transform.smoothscale(icon, (30, 30))
                    self.difficulty_icons[idx] = icon
                    print(f"[LOAD] Loaded difficulty icon: {filename}")
                except Exception as e:
                    print(f"[LOAD-ERR] Failed to load {filename}: {e}")
                    self.difficulty_icons[idx] = None
            else:
                self.difficulty_icons[idx] = None

        DIFFICULTY_LABELS = ["Dễ", "Trung bình", "Khó"]

        for i, label in enumerate(DIFFICULTY_LABELS):
            button_rect = pygame.Rect(
                SIDEBAR_X + 20, (i + 2) * MARGIN + 50 + i * 50, SIDEBAR_W - 40, 50)
            self.buttons.append(
                Button(button_rect, label, TEXT_WHITE, LIGHT, lambda i=i: self.set_difficulty(i)))
            self.button_meta.append(("difficulty", i))

        PLAY_SIDES = ["black--sm.svg", "random.svg", "white--sm.svg"]

        for i, image in enumerate(PLAY_SIDES):
            IMAGE = pygame.image.load("ui/assets/" + image).convert()
            IMAGE = pygame.transform.scale(IMAGE, (25, 25))
            rect = pygame.Rect(SIDEBAR_X + SIDEBAR_W -
                               ((i + 1) * 25 + 10 + i * 8), SIDEBAR_H + MARGIN - 110, 25, 25)

            play_side_val = 2 - i
            self.buttons.append(
                Button(rect, IMAGE, TEXT_WHITE, TEXT_WHITE, lambda i=i, val=play_side_val: self.set_play_side(val)))
            self.button_meta.append(("play_side", play_side_val))

        # nút "Chơi"
        self.play_button_rect = pygame.Rect(
            SIDEBAR_X + 10, SIDEBAR_H + MARGIN - 70, SIDEBAR_W - 20, 60)

        # nút ván mới & undo (khi đã started)
        self.newgame_rect = pygame.Rect(
            SIDEBAR_X + 10, SIDEBAR_H + MARGIN - 70, (SIDEBAR_W - 30) // 2, 60)
        self.undo_rect = pygame.Rect(
            SIDEBAR_X + 20 + (SIDEBAR_W - 30) // 2, SIDEBAR_H + MARGIN - 70, (SIDEBAR_W - 30) // 2, 60)

    def set_play_side(self, i):
        self.play_side = i
        if i == 0:
            self.human_color = 'w'
        elif i == 2:
            self.human_color = 'b'
        print(f"[SIDEBAR] play_side={i}, human_color={self.human_color}")

    def set_difficulty(self, i):
        self.difficulty = i

    def _draw_shadow(self, screen, rect, blur=8, offset=(4, 4), alpha=100):

        shadow_surface = pygame.Surface(
            (rect.width + blur * 2, rect.height + blur * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(blur, blur, rect.width, rect.height)

        # Vẽ shadow với gradient (từ trong ra ngoài mờ dần)
        for i in range(blur):
            alpha_val = int(alpha * (1 - i / blur))
            shadow_color = (0, 0, 0, alpha_val)
            expanded_rect = shadow_rect.inflate(i * 2, i * 2)
            pygame.draw.rect(shadow_surface, shadow_color, expanded_rect)

        screen.blit(shadow_surface, (rect.x - blur +
                    offset[0], rect.y - blur + offset[1]))

    def _draw_depth_effect(self, screen, rect, radius=3):

        # Vẽ border highlight (sáng) ở trên và trái
        highlight_color = (255, 255, 255, 40)
        # Top border
        pygame.draw.line(screen, highlight_color,
                         (rect.left + radius, rect.top),
                         (rect.right - radius, rect.top), 2)
        # Left border
        pygame.draw.line(screen, highlight_color,
                         (rect.left, rect.top + radius),
                         (rect.left, rect.bottom - radius), 2)

        # Vẽ border shadow (tối) ở dưới và phải
        shadow_color = (0, 0, 0, 80)  # Black với alpha
        # Bottom border
        pygame.draw.line(screen, shadow_color,
                         (rect.left + radius, rect.bottom - 1),
                         (rect.right - radius, rect.bottom - 1), 2)
        # Right border
        pygame.draw.line(screen, shadow_color,
                         (rect.right - 1, rect.top + radius),
                         (rect.right - 1, rect.bottom - radius), 2)

    def draw(self, screen):
        font = pygame.font.SysFont("Roboto", 28, bold=True)
        small_font = pygame.font.SysFont("Roboto", 22, bold=False)

        RADIUS = 3

        # Sidebar wrapper - trong suốt với shadow và depth effect
        wrapper_rect = pygame.Rect(
            SIDEBAR_X, MARGIN, SIDEBAR_W, SIDEBAR_H)

        # Vẽ shadow lớn cho sidebar để tạo độ khối
        self._draw_shadow(screen, wrapper_rect, blur=15,
                          offset=(8, 8), alpha=180)

        # Vẽ sidebar background với alpha (bán trong suốt)
        sidebar_surface = pygame.Surface(
            (wrapper_rect.width, wrapper_rect.height), pygame.SRCALPHA)
        sidebar_bg = (45, 45, 45, 180)  # Dark grey với alpha
        pygame.draw.rect(sidebar_surface, sidebar_bg, (0, 0, wrapper_rect.width, wrapper_rect.height),
                         border_radius=RADIUS)
        screen.blit(sidebar_surface, wrapper_rect.topleft)

        # Vẽ depth effect cho sidebar (border highlight/shadow)
        self._draw_depth_effect(screen, wrapper_rect, radius=RADIUS)

        # Header với shadow và depth
        header_rect = pygame.Rect(
            SIDEBAR_X, MARGIN, SIDEBAR_W, 50)

        # Vẽ shadow cho header
        self._draw_shadow(screen, header_rect, blur=8,
                          offset=(3, 3), alpha=140)

        # Vẽ header với background trong suốt một phần
        header_surface = pygame.Surface(
            (header_rect.width, header_rect.height), pygame.SRCALPHA)
        header_bg = (35, 35, 35, 220)  # Dark grey với alpha
        pygame.draw.rect(header_surface, header_bg, (0, 0, header_rect.width, header_rect.height),
                         border_top_left_radius=RADIUS, border_top_right_radius=RADIUS)
        screen.blit(header_surface, header_rect.topleft)

        # Vẽ depth effect cho header
        self._draw_depth_effect(screen, header_rect, radius=RADIUS)

        icon_text = font.render("Play Bots", True, TEXT_WHITE)
        icon_text_rect = icon_text.get_rect(center=header_rect.center)
        screen.blit(icon_text, icon_text_rect)

        if not self.started:
            # Hiển thị lựa chọn trước khi bấm "Chơi"
            for i, button in enumerate(self.buttons):
                kind, value = self.button_meta[i]
                active = False
                if kind == "difficulty":
                    active = (value == self.difficulty)
                elif kind == "play_side":
                    active = (value == self.play_side)

                # Draw button with custom styling for difficulty buttons
                if kind == "difficulty":
                    self._draw_difficulty_button(screen, button, value, active)
                else:
                    button.draw(screen, active=active)

            # Vẽ shadow cho nút "Chơi"
            self._draw_shadow(screen, self.play_button_rect,
                              blur=8, offset=(4, 4), alpha=120)

            # Draw play button - dark grey với alpha
            play_surface = pygame.Surface(
                (self.play_button_rect.width, self.play_button_rect.height), pygame.SRCALPHA)
            play_bg = (45, 45, 45, 220)  # Dark grey với alpha
            pygame.draw.rect(play_surface, play_bg, (0, 0, self.play_button_rect.width, self.play_button_rect.height),
                             border_radius=RADIUS)
            screen.blit(play_surface, self.play_button_rect.topleft)

            # Vẽ depth effect cho nút "Chơi"
            self._draw_depth_effect(
                screen, self.play_button_rect, radius=RADIUS)

            text = font.render("Chơi", True, TEXT_WHITE)
            text_rect = text.get_rect(center=self.play_button_rect.center)

            screen.blit(text, text_rect)
        else:
            # Hiển thị log nước đi
            y = MARGIN + 70
            line_h = 32
            max_lines = self.max_lines  # max visible lines before scrolling
            start_idx = self.scroll_offset
            end_idx = start_idx + max_lines

            for idx, (w_mv, b_mv) in enumerate(self.move_log, start=1):
                if idx < start_idx + 1 or idx > end_idx:
                    continue  # skip if outside visible range
                num_txt = small_font.render(f"{idx}.", True, TEXT_WHITE)
                w_txt = small_font.render(w_mv or "", True, TEXT_WHITE)
                b_txt = small_font.render(b_mv or "", True, TEXT_WHITE)
                screen.blit(num_txt, (SIDEBAR_X + 20, y))
                screen.blit(w_txt, (SIDEBAR_X + 55, y))
                screen.blit(b_txt, (SIDEBAR_X + 170, y))
                y += line_h

            # Draw scrollbar
            scrollbar_x = SIDEBAR_X + SIDEBAR_W - 20
            scrollbar_y = MARGIN + 70
            scrollbar_h = self.max_lines * line_h
            scrollbar_track = pygame.Rect(
                scrollbar_x, scrollbar_y, 10, scrollbar_h)
            pygame.draw.rect(screen, (100, 100, 100),
                             scrollbar_track)  # grey track
            if len(self.move_log) > self.max_lines:
                visible_ratio = self.max_lines / len(self.move_log)
                thumb_h = scrollbar_h * visible_ratio
                scroll_ratio = self.scroll_offset / \
                    (len(self.move_log) - self.max_lines)
                thumb_y = scrollbar_y + scroll_ratio * (scrollbar_h - thumb_h)
                thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_h)
                pygame.draw.rect(screen, TEXT_WHITE, thumb_rect)

            # Vẽ shadow cho các nút
            self._draw_shadow(screen, self.newgame_rect,
                              blur=8, offset=(4, 4), alpha=120)
            self._draw_shadow(screen, self.undo_rect, blur=8,
                              offset=(4, 4), alpha=120)

            # nút ván mới và undo với alpha
            new_surface = pygame.Surface(
                (self.newgame_rect.width, self.newgame_rect.height), pygame.SRCALPHA)
            undo_surface = pygame.Surface(
                (self.undo_rect.width, self.undo_rect.height), pygame.SRCALPHA)
            button_bg = (35, 155, 55, 240)  # Green với alpha
            pygame.draw.rect(new_surface, button_bg, (0, 0, self.newgame_rect.width, self.newgame_rect.height),
                             border_radius=RADIUS)
            pygame.draw.rect(undo_surface, button_bg, (0, 0, self.undo_rect.width, self.undo_rect.height),
                             border_radius=RADIUS)
            screen.blit(new_surface, self.newgame_rect.topleft)
            screen.blit(undo_surface, self.undo_rect.topleft)

            # Vẽ depth effect cho các nút
            self._draw_depth_effect(screen, self.newgame_rect, radius=RADIUS)
            self._draw_depth_effect(screen, self.undo_rect, radius=RADIUS)

            new_txt = font.render("Ván mới", True, TEXT_WHITE)
            undo_txt = font.render("Undo", True, TEXT_WHITE)
            screen.blit(new_txt, new_txt.get_rect(
                center=self.newgame_rect.center))
            screen.blit(undo_txt, undo_txt.get_rect(
                center=self.undo_rect.center))

    def handle_event(self, ev):
        if not self.started:
            for btn in self.buttons:
                btn.handle_event(ev)

            # click nút "Chơi"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.play_button_rect.collidepoint(ev.pos):
                    if self.on_start:
                        self.on_start()
        else:
            # --- NEW: handle scroll wheel for move log ---
            if ev.type == pygame.MOUSEWHEEL:
                # scroll_y: positive = scroll up, negative = scroll down
                if ev.y > 0:  # scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                else:  # scroll down
                    max_offset = max(0, len(self.move_log) - self.max_lines)
                    self.scroll_offset = min(
                        max_offset, self.scroll_offset + 1)
                return

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.newgame_rect.collidepoint(ev.pos):
                    if self.on_new_game:
                        self.on_new_game()
                elif self.undo_rect.collidepoint(ev.pos):
                    if self.on_undo:
                        self.on_undo()

    def set_on_start(self, cb):
        self.on_start = cb

    def set_on_new_game(self, cb):
        self.on_new_game = cb

    def set_on_undo(self, cb):
        self.on_undo = cb

    # ====== GAME STATE HELPERS ======
    def start_game(self):
        self.started = True
        self.move_log = []
        self.scroll_offset = 0  # reset scroll when new game starts

    def add_move(self, color, move_str):
        if color == 'w':
            self.move_log.append([move_str, ""])
        else:
            if not self.move_log:
                self.move_log.append(["", move_str])
            else:
                self.move_log[-1][1] = move_str
        # Auto-scroll to latest move
        self.scroll_offset = max(0, len(self.move_log) - self.max_lines)

    def undo_move(self, color):
        if not self.move_log:
            return
        if color == 'b':
            self.move_log[-1][1] = ""
            if self.move_log[-1][0] == "":
                self.move_log.pop()
        else:
            self.move_log.pop()
        # Adjust scroll offset if necessary
        self.scroll_offset = min(self.scroll_offset, max(
            0, len(self.move_log) - self.max_lines))

    def stop_game(self):
        self.started = False
        self.move_log = []

    def _draw_difficulty_button(self, screen, button, difficulty_idx, active):
        """Draw difficulty button with icon and arrow"""
        font = pygame.font.SysFont("Roboto", 28, bold=True)

        # Vẽ shadow cho button (mạnh hơn nếu active)
        shadow_blur = 8 if active else 6
        shadow_alpha = 120 if active else 90
        self._draw_shadow(screen, button.rect, blur=shadow_blur,
                          offset=(4, 4), alpha=shadow_alpha)

        # Button background color với alpha - green if active, otherwise darker grey
        if active:
            bg_color = (35, 155, 55, 240)  # Green for active với alpha
            text_color = TEXT_WHITE
        else:
            bg_color = (45, 45, 45, 220)  # Dark grey for inactive với alpha
            text_color = TEXT_WHITE

        # Draw button background với alpha
        button_surface = pygame.Surface(
            (button.rect.width, button.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, bg_color, (0, 0,
                         button.rect.width, button.rect.height), border_radius=3)
        screen.blit(button_surface, button.rect.topleft)

        # Vẽ depth effect cho button
        self._draw_depth_effect(screen, button.rect, radius=3)

        # Draw border if active (green border)
        if active:
            border_surface = pygame.Surface(
                (button.rect.width + 12, button.rect.height + 12), pygame.SRCALPHA)
            border_color = (35, 155, 55, 200)
            pygame.draw.rect(border_surface, border_color, (0, 0, button.rect.width + 12, button.rect.height + 12),
                             width=3, border_radius=6)
            screen.blit(border_surface, (button.rect.x - 6, button.rect.y - 6))

        # Draw icon if available
        icon = self.difficulty_icons.get(difficulty_idx)
        icon_x = button.rect.left + 15
        icon_y = button.rect.centery

        if icon:
            icon_rect = icon.get_rect(center=(icon_x, icon_y))
            screen.blit(icon, icon_rect)
            text_x = icon_x + 40  # Text starts after icon
        else:
            text_x = button.rect.left + 15

        # Draw text
        text = font.render(button.text, True, text_color)
        text_rect = text.get_rect(midleft=(text_x, button.rect.centery))
        screen.blit(text, text_rect)

        # Draw arrow if active
        if active:
            arrow_size = 20
            arrow_x = button.rect.right - 25
            arrow_y = button.rect.centery
            # Draw right-pointing arrow (triangle)
            arrow_points = [
                (arrow_x, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size, arrow_y),
                (arrow_x, arrow_y + arrow_size // 2)
            ]
            pygame.draw.polygon(screen, text_color, arrow_points)
