import pygame


class Button:
    def __init__(self, rect, text, text_color, box_color, callback, active_color=(0, 200, 0), border_width=3):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.text_color = text_color
        self.box_color = box_color
        self.callback = callback
        self.active_color = active_color
        self.border_width = border_width

    def draw(self, screen, active=False):
        font = pygame.font.SysFont("Roboto", 28, bold=True)

        pygame.draw.rect(
            screen, self.box_color, self.rect, border_radius=3)

        if active:
            pygame.draw.rect(
                screen,
                self.active_color,
                self.rect.inflate(6, 6),
                width=self.border_width,
                border_radius=6,
            )

        if (isinstance(self.text, str)):
            text = font.render(self.text, True, self.text_color)
        else:
            text = self.text

        text_rect = text.get_rect(center=self.rect.center)

        screen.blit(text, text_rect)

    def handle_event(self, ev):

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                self.callback()
