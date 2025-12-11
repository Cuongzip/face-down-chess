import pygame
from constants import MARGIN, PLAYER_SIZE, BOARD_SIZE, TEXT_WHITE


DIFFICULTY_LABELS = ["Dễ", "Trung bình", "Khó"]


class PlayerPanel:
    """
    Vẽ thông tin người chơi (Bot/Me) ở trên và dưới bàn cờ.
    """

    def __init__(self, font: pygame.font.Font):
        self.font = font

    def draw(self, screen, sidebar):
        box_size = PLAYER_SIZE - 8
        top_y = MARGIN + (PLAYER_SIZE - box_size) // 2
        bottom_y = MARGIN + PLAYER_SIZE + BOARD_SIZE + (PLAYER_SIZE - box_size) // 2

        bot_rect = pygame.Rect(MARGIN, top_y, box_size, box_size)
        me_rect = pygame.Rect(MARGIN, bottom_y, box_size, box_size)

        pygame.draw.rect(screen, (210, 210, 210), bot_rect, border_radius=4)
        pygame.draw.rect(screen, (210, 210, 210), me_rect, border_radius=4)

        diff_idx = getattr(sidebar, "difficulty", 1)
        if 0 <= diff_idx < len(DIFFICULTY_LABELS):
            diff_label = DIFFICULTY_LABELS[diff_idx]
        else:
            diff_label = "Bot"

        bot_text = self.font.render(f"BOT ({diff_label})", True, TEXT_WHITE)
        me_text = self.font.render("Me", True, TEXT_WHITE)

        screen.blit(
            bot_text,
            (bot_rect.right + 12, top_y + box_size // 2 - bot_text.get_height() // 2),
        )
        screen.blit(
            me_text,
            (me_rect.right + 12, bottom_y + box_size // 2 - me_text.get_height() // 2),
        )

