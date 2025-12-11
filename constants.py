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


# color palette (shared)
BG = (15, 28, 48)

# board squares
LIGHT = (245, 245, 200)
DARK = (180, 120, 80)

# piece / UI colors
CIRCLE = (100, 100, 100)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (0, 0, 0)

# highlights
HIGHLIGHT = (0, 255, 0, 120)

# sidebar specific aliases (can be overridden if needed)
SIDEBAR_BG = (13, 21, 34)
SIDEBAR_HEADER = (179, 122, 76)
SIDEBAR_TEXT = TEXT_WHITE
SIDEBAR_ACCENT = (28, 180, 80)  # play button color
