import pygame
from ui.button import Button
from constants import MARGIN, SIDEBAR_X, LIGHT, DARK, SIDEBAR_W, SIDEBAR_H, TEXT_WHITE


class Sidebar:
    def __init__(self):
        self.buttons = []
        self.button_meta = []  # (kind, value)
        self.difficulty = 1
        self.play_side = 0
        self.human_color = 'w'  # default to white; can be changed via UI color selector
        self.on_start = None  # callback khi nhấn nút "Chơi"
        self.on_new_game = None
        self.on_undo = None
        self.started = False
        self.move_log = []  # list[[w_move, b_move]]
        self.scroll_offset = 0  # for scrollable move log
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
            # map button index to play_side value: [black(2), random(1), white(0)]
            # i=0->2(black), i=1->1(random), i=2->0(white)
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
        # Auto-update human_color based on play_side (0=white, 1=random, 2=black)
        if i == 0:
            self.human_color = 'w'
        elif i == 2:
            self.human_color = 'b'
        # i == 1 (random): don't change human_color here, let reset_game handle it
        print(f"[SIDEBAR] play_side={i}, human_color={self.human_color}")

    def set_difficulty(self, i):
        self.difficulty = i

    def draw(self, screen):
        font = pygame.font.SysFont("Roboto", 28, bold=True)
        small_font = pygame.font.SysFont("Roboto", 22, bold=False)

        RADIUS = 3
        wrapper_rect = pygame.Rect(
            SIDEBAR_X, MARGIN, SIDEBAR_W, SIDEBAR_H)
        pygame.draw.rect(screen, (38, 37, 34), wrapper_rect,
                         width=0, border_radius=RADIUS)

        header_rect = pygame.Rect(
            SIDEBAR_X, MARGIN, SIDEBAR_W, 50)

        pygame.draw.rect(screen, DARK, header_rect, border_top_left_radius=RADIUS,
                         border_top_right_radius=RADIUS)

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
                button.draw(screen, active=active)

            pygame.draw.rect(
                screen, DARK, self.play_button_rect, border_radius=RADIUS)

            text = font.render("Chơi", True, TEXT_WHITE)
            text_rect = text.get_rect(center=self.play_button_rect.center)

            screen.blit(text, text_rect)
        else:
            # Hiển thị log nước đi
            y = MARGIN + 70
            line_h = 32
            max_lines = 10  # max visible lines before scrolling
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

            # nút ván mới và undo
            pygame.draw.rect(screen, (35, 155, 55),
                             self.newgame_rect, border_radius=RADIUS)
            pygame.draw.rect(screen, (35, 155, 55),
                             self.undo_rect, border_radius=RADIUS)
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
                    max_offset = max(0, len(self.move_log) - 10)
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

    def undo_move(self, color):
        if not self.move_log:
            return
        if color == 'b':
            self.move_log[-1][1] = ""
            if self.move_log[-1][0] == "":
                self.move_log.pop()
        else:
            self.move_log.pop()

    def stop_game(self):
        self.started = False
        self.move_log = []
