from chess_to_the_death.util.loader import loadImage


class Piece:
    image = None
    firstMove = True

    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        self._name = name
        self.cell_col = cell_col
        self.cell_row = cell_row
        self._player = player
        if image_size:
            self.image = loadImage(player + name, image_size)

    def move(self, x: int, y: int) -> None:
        """
        move the piece to the new coordinates x,y.
        """
        self.firstMove = False
        self.cell_col = x
        self.cell_row = y

    def isEnemy(self, x: int, y: int, board) -> bool:
        """
        Checks whether a piece on the numpy-array board
        on the coordinates x,y is an enemy or not.
        """
        return (self._player == 'white' and board[y, x] < 0) or (
            self._player == 'black' and board[y, x] > 0)

    def getOptions(self, board, flip=True) -> tuple:
        """
        Takes a numpy-array board and returns a tuple containing
        two lists. The lists contain tuples of valid movement-moves
        and valid attack-moves.
        """
        return ([], [])

    def __repr__(self) -> str:
        return self._player + self._name + " (" + hex(id(self)) + ")"


class Rook(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 90
        self.damage = 15

    def getOptions(self, board, _=True):
        options_move, options_attack = [], []
        options = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for option in options:
            for i in range(1, max(board.shape[0], board.shape[1])):
                x, y = self.cell_col + i * \
                    option[0], self.cell_row + i * option[1]
                if not ((0 <= y < board.shape[0]) and (
                        0 <= x < board.shape[1])):
                    break
                if board[y, x] != 0:
                    if super().isEnemy(x, y, board):
                        options_attack.append((x, y))
                    break
                options_move.append((x, y))

        return (options_move, options_attack)


class Knight(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 32
        self.damage = 45

    def getOptions(self, board, _=True):
        options_move, options_attack = [], []
        options = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for option in options:
            x, y = self.cell_col + option[0], self.cell_row + option[1]
            if not ((0 <= x < board.shape[1]) and (
                    0 <= y < board.shape[0])):
                continue
            if board[y, x] != 0:
                if super().isEnemy(x, y, board):
                    options_attack.append((x, y))
                    continue
            if board[y, x] == 0:
                options_move.append((x, y))

        return (options_move, options_attack)


class Bishop(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 45
        self.damage = 32

    def getOptions(self, board, _=True):
        options_move, options_attack = [], []
        options = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for option in options:
            for i in range(1, max(board.shape[0], board.shape[1])):
                x, y = self.cell_col + i * \
                    option[0], self.cell_row + i * option[1]
                if not ((0 <= x < board.shape[1]) and (
                        0 <= y < board.shape[0])):
                    break
                if board[y, x] != 0:
                    if super().isEnemy(x, y, board):
                        options_attack.append((x, y))
                    break
                options_move.append((x, y))

        return (options_move, options_attack)


class Pawn(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 120
        self.damage = 120

    def getOptions(self, board, flip=True):
        options_move, options_attack = [], []
        options_m, options_a = [(0, -1), (0, -2)], [(-1, -1), (1, -1)]
        if not flip:
            options_a = [(-x, -y) for x,y in options_a]
            options_m = [(-x, -y) for x,y in options_m]
        for option_a in options_a:
            x, y = self.cell_col + option_a[0], self.cell_row + option_a[1]
            if not ((0 <= x < board.shape[1]) and (
                    0 <= y < board.shape[0])):
                continue
            if board[y, x] != 0:
                if super().isEnemy(x, y, board):
                    options_attack.append((x, y))
        
        if 0 <= self.cell_row+options_m[0][1] < board.shape[0]:
            if board[self.cell_row+options_m[0][1], self.cell_col] == 0:
                options_move.append((self.cell_col, self.cell_row+options_m[0][1]))
        if 0 <= self.cell_row+options_m[1][1] < board.shape[0] and self.firstMove:
            if board[self.cell_row+options_m[1][1], self.cell_col] == 0:
                options_move.append((self.cell_col, self.cell_row+options_m[1][1]))

        return (options_move, options_attack)


class Queen(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 10
        self.damage = 60

    def getOptions(self, board, _=True):
        options_move, options_attack = [], []
        m, a = Bishop('b', self.cell_col, self.cell_row,
                      self._player, None).getOptions(board)
        options_move += m
        options_attack += a
        m, a = Rook('r', self.cell_col, self.cell_row,
                    self._player, None).getOptions(board)
        options_move += m
        options_attack += a

        return (options_move, options_attack)


class King(Piece):
    def __init__(self, name, cell_col, cell_row, player, image_size=None):
        super().__init__(name, cell_col, cell_row, player, image_size)
        self.maxHealth = self.health = 150
        self.damage = 35

    def getOptions(self, board, _=True):
        options_move, options_attack = [], []
        options = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                   (0, 1), (1, -1), (1, 0), (1, 1)]
        for option in options:
            x, y = self.cell_col + option[0], self.cell_row + option[1]
            if not ((0 <= x < board.shape[1]) and (
                    0 <= y < board.shape[0])):
                continue
            if board[y, x] != 0:
                if super().isEnemy(x, y, board):
                    options_attack.append((x, y))
                    continue
            if board[y, x] == 0:
                options_move.append((x, y))

        return (options_move, options_attack)
