
class Piece:
    image = None

    def __init__(self, name, cell_x, cell_y, player):
        self._name = name
        self.cell_x = cell_x
        self.cell_y = cell_y
        self._player = player

    def move(self, x, y):
        self.cell_x = x
        self.cell_y = y
    
    def isEnemy(self, x, y, board):
        return (self._player == 'white' and board[x, y] < 0) or (
                self._player == 'black' and board[x, y] > 0)

    def getOptions(self, board):
        return ([], [])

    def __repr__(self):
        return self._player + self._name + " (" + hex(id(self)) + ")"


class Rook(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10

    def getOptions(self, board):
        options_move, options_attack = [], []
        for i in range(1, board.shape[0]):
            if self.cell_y+i >= board.shape[0]:
                break
            if board[self.cell_y+i, self.cell_x] != 0:
                if super().isEnemy(self.cell_y+i, self.cell_x, board):
                    options_attack.append((self.cell_y+i, self.cell_x))
                break
            options_move.append((self.cell_y+i, self.cell_x))
        for i in range(1, board.shape[0]):
            if self.cell_y-i < 0:
                break
            if board[self.cell_y-i, self.cell_x] != 0:
                if super().isEnemy(self.cell_y-i, self.cell_x, board):
                    options_attack.append((self.cell_y-i, self.cell_x))
                break
            options_move.append((self.cell_y-i, self.cell_x))
        for i in range(1, board.shape[0]):
            if self.cell_x+i >= board.shape[1]:
                break
            if board[self.cell_y, self.cell_x+i] != 0:
                if super().isEnemy(self.cell_y, self.cell_x+i, board):
                    options_attack.append((self.cell_y, self.cell_x+i))
                break
            options_move.append((self.cell_y, self.cell_x+i))
        for i in range(1, board.shape[0]):
            if self.cell_x-i < 0:
                break
            if board[self.cell_y, self.cell_x-i] != 0:
                if super().isEnemy(self.cell_y, self.cell_x-i, board):
                    options_attack.append((self.cell_y, self.cell_x-i))
                break
            options_move.append((self.cell_y, self.cell_x-i))

        return (options_move, options_attack)

class Knight(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10
        
    def getOptions(self, board):
        options_move, options_attack = [], []
        options = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for option in options:
            if (self.cell_y+option[0] >= board.shape[0]) or (
                self.cell_x+option[1] >= board.shape[1]) or (
                self.cell_y+option[0] < 0) or (
                self.cell_x+option[1] < 0):
                continue
            if board[self.cell_y+option[0], self.cell_x+option[1]] != 0:
                if super().isEnemy(self.cell_y+option[0], self.cell_x+option[1], board):
                    options_attack.append((self.cell_y+option[0], self.cell_x+option[1]))
                    continue
            if board[self.cell_y+option[0], self.cell_x+option[1]] == 0:
                options_move.append((self.cell_y+option[0], self.cell_x+option[1]))
        
        return (options_move, options_attack)
        


class Bishop(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10

    def getOptions(self, board):
        options_move, options_attack = [], []
        for i in range(1, board.shape[0]):
            if self.cell_y+i >= board.shape[0] or self.cell_x+i >= board.shape[1]:
                break
            if board[self.cell_y+i, self.cell_x+i] != 0:
                if super().isEnemy(self.cell_y+i, self.cell_x+i, board):
                    options_attack.append((self.cell_y+i, self.cell_x+i))
                break
            options_move.append((self.cell_y+i, self.cell_x+i))
        for i in range(1, board.shape[0]):
            if self.cell_y-i < 0 or self.cell_x-i < 0:
                break
            if board[self.cell_y-i, self.cell_x-i] != 0:
                if super().isEnemy(self.cell_y-i, self.cell_x-i, board):
                    options_attack.append((self.cell_y-i, self.cell_x-i))
                break
            options_move.append((self.cell_y-i, self.cell_x-i))
        for i in range(1, board.shape[0]):
            if self.cell_y+i >= board.shape[0] or self.cell_x-i < 0:
                break
            if board[self.cell_y+i, self.cell_x-i] != 0:
                if super().isEnemy(self.cell_y+i, self.cell_x-i, board):
                    options_attack.append((self.cell_y+i, self.cell_x-i))
                break
            options_move.append((self.cell_y+i, self.cell_x-i))
        for i in range(1, board.shape[0]):
            if self.cell_y-i < 0 or self.cell_x+i >= board.shape[1]:
                break
            if board[self.cell_y-i, self.cell_x+i] != 0:
                if super().isEnemy(self.cell_y-i, self.cell_x+i, board):
                    options_attack.append((self.cell_y-i, self.cell_x+i))
                break
            options_move.append((self.cell_y-i, self.cell_x+i))

        return (options_move, options_attack)


class Pawn(Piece):
    firstMove = True
    
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10
        
    def getOptions(self, board):
        options_move, options_attack = [], []
        if self.cell_y-1 >= 0 and self.cell_x-1 >= 0:
            if super().isEnemy(self.cell_y-1, self.cell_x-1, board):
                options_attack.append((self.cell_y-1, self.cell_x-1))
        if self.cell_y-1 >= 0 and self.cell_x+1 < board.shape[1]:
            if super().isEnemy(self.cell_y-1, self.cell_x+1, board):
                options_attack.append((self.cell_y-1, self.cell_x+1))
        if self.cell_y-1 >= 0:
            if board[self.cell_y-1, self.cell_x] == 0:
                options_move.append((self.cell_y-1, self.cell_x))
        if self.cell_y-2 >= 0 and self.firstMove:
            if board[self.cell_y-2, self.cell_x] == 0:
                options_move.append((self.cell_y-2, self.cell_x))
        return (options_move, options_attack)
    
    def move(self, x, y):
        self.firstMove = False
        return super().move(x, y)


class Queen(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10

    def getOptions(self, board):
            options_move, options_attack = [], []
            m, a = Bishop('b', self.cell_x, self.cell_y, self._player).getOptions(board)
            options_move += m
            options_attack += a
            m, a = Rook('r', self.cell_x, self.cell_y, self._player).getOptions(board)
            options_move += m
            options_attack += a
            
            return (options_move, options_attack)

class King(Piece):
    def __init__(self, name, cell_x, cell_y, player):
        super().__init__(name, cell_x, cell_y, player)
        self.maxHealth = self.health = 100
        self.damage = 10
        
    def getOptions(self, board):
        options_move, options_attack = [], []
        options = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                   (0, 1), (1, -1), (1, 0), (1, 1)]
        for option in options:
            if (self.cell_y+option[0] >= board.shape[0]) or (
                self.cell_x+option[1] >= board.shape[1]) or (
                self.cell_y+option[0] < 0) or (
                self.cell_x+option[1] < 0):
                continue
            if board[self.cell_y+option[0], self.cell_x+option[1]] != 0:
                if super().isEnemy(self.cell_y+option[0], self.cell_x+option[1], board):
                    options_attack.append((self.cell_y+option[0], self.cell_x+option[1]))
                    continue
            if board[self.cell_y+option[0], self.cell_x+option[1]] == 0:
                options_move.append((self.cell_y+option[0], self.cell_x+option[1]))
        
        return (options_move, options_attack)
