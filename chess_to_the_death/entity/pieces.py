from chess_to_the_death.util.loader import loadImage
from chess_to_the_death.util.definition import PieceChar

class Piece:
    _name = PieceChar.UNDEFINED
    
    def __init__(self, cell_pos: tuple, player: str, image_size: tuple = None):
        self.setPos(cell_pos)
        self._player = player
        
        self.firstMove = True
        self.loadImage(image_size)

    def loadImage(self, image_size: tuple = None) -> None:
        """
        load the image to diplay the piece
        """
        self.image = loadImage(self._player + self._name, image_size)
        
    def getPos(self) -> tuple:
        return (self.cell_col, self.cell_row)
    
    def setPos(self, to_pos: tuple) -> None:
        self.cell_col, self.cell_row = to_pos

    def move(self, to_pos: tuple) -> None:
        """
        move the piece to the new coordinates x,y.
        """
        self.firstMove = False
        self.setPos(to_pos)

    def isEnemy(self, x: int, y: int, board) -> bool:
        """
        Checks whether a piece on the numpy-array board
        on the coordinates x,y is an enemy or not.
        """
        return ((board[y, x] * board[self.cell_row, self.cell_col]) < 0)

    def getOptions(self, board, flip: bool = True) -> tuple:
        """
        Takes a numpy-array board and returns a tuple containing
        two lists. The lists contain tuples of valid movement-moves
        and valid attack-moves.
        """
        return ([], [])
    
    def __repr__(self) -> str:
        return self._player + self._name + " (" + hex(id(self)) + ")"


class Rook(Piece):
    _name = PieceChar.ROOK
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
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
    _name = PieceChar.KNIGHT
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
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
            if super().isEnemy(x, y, board):
                options_attack.append((x, y))
                continue
            if board[y, x] == 0:
                options_move.append((x, y))

        return (options_move, options_attack)


class Bishop(Piece):
    _name = PieceChar.BISHOP
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
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
    _name = PieceChar.PAWN
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
        self.maxHealth = self.health = 120
        self.damage = 120

    def getOptions(self, board, flip):
        options_move, options_attack = [], []
        options_m, options_a = [(0, -1), (0, -2)], [(-1, -1), (1, -1)]
        if flip:
            options_a = [(-x, -y) for x,y in options_a]
            options_m = [(-x, -y) for x,y in options_m]
        for option_a in options_a:
            x, y = self.cell_col + option_a[0], self.cell_row + option_a[1]
            if not ((0 <= x < board.shape[1]) and (
                    0 <= y < board.shape[0])):
                continue
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
    _name = PieceChar.QUEEN
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
        self.maxHealth = self.health = 10
        self.damage = 60

    def getOptions(self, board, _=True):
        return tuple([a+b for a,b in \
            list(zip(
                Bishop(self.getPos(), self._player, None).getOptions(board),
                Rook(self.getPos(), self._player, None).getOptions(board)
            ))])


class King(Piece):
    _name = PieceChar.KING
    
    def __init__(self, cell_pos, player, image_size=None):
        super().__init__(cell_pos, player, image_size)
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
            if super().isEnemy(x, y, board):
                options_attack.append((x, y))
                continue
            if board[y, x] == 0:
                options_move.append((x, y))

        return (options_move, options_attack)
