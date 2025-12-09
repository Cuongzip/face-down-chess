# game/conceal.py
class Piece:
    def __init__(self, true_type: str, start_type: str, color: str, isKing: bool = False):
        """
        true_type: 'P','N','B','R','Q','K'  -- loại thật
        start_type: loại khi úp (dùng để tính nước đi khi còn úp)
        color: 'w' or 'b' (white/black)
        isKing: nếu True -> luôn lộ (isFaceDown=False)
        """
        self.true_type = true_type
        self.start_type = start_type
        self.color = color  # 'w' or 'b'
        self.isKing = isKing
        # vua luôn lộ
        self.isFaceDown = False if isKing else True

    def flip(self):
        """Lật quân: từ úp -> lộ. Không lật ngược lại."""
        if self.isFaceDown:
            self.isFaceDown = False

    def __repr__(self):
        return f"Piece(true={self.true_type}, start={self.start_type}, color={self.color}, FD={self.isFaceDown})"
