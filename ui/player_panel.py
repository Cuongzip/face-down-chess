import pygame
from constants import MARGIN, PLAYER_SIZE, BOARD_SIZE, TEXT_WHITE


DIFFICULTY_LABELS = ["Dễ", "Trung bình", "Khó"]


class PlayerPanel:

    def __init__(self, font: pygame.font.Font, user_avatar=None, bot_icons=None):
        self.font = font
        self.user_avatar = user_avatar
        self.bot_icons = bot_icons or {}

    def draw(self, screen, sidebar):
        box_size = PLAYER_SIZE - 8
        top_y = MARGIN + (PLAYER_SIZE - box_size) // 2
        bottom_y = MARGIN + PLAYER_SIZE + \
            BOARD_SIZE + (PLAYER_SIZE - box_size) // 2

        bot_rect = pygame.Rect(MARGIN, top_y, box_size, box_size)
        me_rect = pygame.Rect(MARGIN, bottom_y, box_size, box_size)

        # Vẽ background cho avatar boxes
        pygame.draw.rect(screen, (210, 210, 210), bot_rect, border_radius=4)
        pygame.draw.rect(screen, (210, 210, 210), me_rect, border_radius=4)

        # Vẽ bot avatar (icon difficulty)
        diff_idx = getattr(sidebar, "difficulty", 1)
        bot_icon = self.bot_icons.get(diff_idx)
        if bot_icon:
            # Scale icon để vừa với box
            icon_size = box_size - 8
            scaled_icon = pygame.transform.smoothscale(
                bot_icon, (icon_size, icon_size))
            icon_rect = scaled_icon.get_rect(center=bot_rect.center)
            screen.blit(scaled_icon, icon_rect)
        else:
            # Fallback: vẽ text nếu không có icon
            fallback_text = self.font.render("BOT", True, (100, 100, 100))
            text_rect = fallback_text.get_rect(center=bot_rect.center)
            screen.blit(fallback_text, text_rect)

        # Vẽ user avatar
        if self.user_avatar:
            # Scale avatar để vừa với box
            avatar_size = box_size - 8
            scaled_avatar = pygame.transform.smoothscale(
                self.user_avatar, (avatar_size, avatar_size))
            avatar_rect = scaled_avatar.get_rect(center=me_rect.center)
            screen.blit(scaled_avatar, avatar_rect)
        else:
            # Fallback: vẽ text nếu không có avatar
            fallback_text = self.font.render("ME", True, (100, 100, 100))
            text_rect = fallback_text.get_rect(center=me_rect.center)
            screen.blit(fallback_text, text_rect)

        # Vẽ text labels
        if 0 <= diff_idx < len(DIFFICULTY_LABELS):
            diff_label = DIFFICULTY_LABELS[diff_idx]
        else:
            diff_label = "Bot"

        bot_text = self.font.render(f"BOT ({diff_label})", True, TEXT_WHITE)
        me_text = self.font.render("Me", True, TEXT_WHITE)

        screen.blit(
            bot_text,
            (bot_rect.right + 12, top_y + box_size //
             2 - bot_text.get_height() // 2),
        )
        screen.blit(
            me_text,
            (me_rect.right + 12, bottom_y + box_size //
             2 - me_text.get_height() // 2),
        )
