
class Piece:
    image = None
    def __init__(self, name, cell_x, cell_y, player):
        self._name = name
        self.cell_x = cell_x
        self.cell_y = cell_y
        self._player = player


class Rook(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10


class Knight(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10


class Bishop(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10


class Pawn(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10


class Queen(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10


class King(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10
