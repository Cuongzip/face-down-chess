class ChessPiece:
    def __init__(self, piece_id, real_type, start_type, owner, position):
        self.piece_id = piece_id
        self.real_type = real_type
        self.start_type = start_type
        self.owner = owner
        self.position = position

        # Nếu là quân Vua và ở đúng vị trí mặc định thì không cần úp
        if (real_type == "King" and
            ((owner == "White" and position == (4, 0)) or
             (owner == "Black" and position == (4, 7)))):
            self.is_face_down = False
        else:
            self.is_face_down = True

        self.has_moved = False

    def flip(self):
        if not self.is_face_down:
            print("Quân đã lật hoặc là Vua, không cần lật.")
            return
        self.is_face_down = False

    def move(self, new_position):
        self.position = new_position
        self.has_moved = True

    def __repr__(self):
        return (f"<{self.owner} {self.real_type} at {self.position}, "
                f"face_down={self.is_face_down}, moved={self.has_moved}>")
