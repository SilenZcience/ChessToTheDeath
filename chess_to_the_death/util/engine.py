import numpy as np
from chess_to_the_death.entity.pieces import *
from chess_to_the_death.entity.player import Player


def bothWayDic(dic: dict) -> dict:
    """
    takes a dictionary and adds every (value, key) entry,
    essentially flipping the given entries.
    """
    dic.update(dict(map(reversed, dic.items())))
    return dic


DIMENSION = (8, 8)
flipDic = bothWayDic({0: 7, 1: 6, 2: 5, 3: 4})
pieceTranslateDic = bothWayDic({'p': 1, 'b': 2, 'n': 3, 'r': 4, 'q': 5, 'k': 6})


class GameState:
    player_turn = True # True -> 'white', False -> 'black'
    board_flipped = False
    flip_board = True
    board: np.ndarray = None
    white_casualties, black_casualties = [], []
    action_log = []
    alpha_identifiers = list(map(chr, range(65, 65+DIMENSION[0])))
    numbers_identifiers = list(map(str, range(DIMENSION[1], 0, -1)))

    def __init__(self, image_size, flip_board):
        self.image_size = image_size
        self.flip_board = flip_board
        
        white_pieces = []
        white_pieces.append(Rook(  'r', 0, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Rook(  'r', 7, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Knight('n', 1, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Knight('n', 6, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Bishop('b', 2, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Bishop('b', 5, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Queen( 'q', 3, 7, Player.PLAYER_W, image_size))
        white_pieces.append(King(  'k', 4, 7, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 0, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 1, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 2, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 3, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 4, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 5, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 6, 6, Player.PLAYER_W, image_size))
        white_pieces.append(Pawn(  'p', 7, 6, Player.PLAYER_W, image_size))

        black_pieces = []
        black_pieces.append(Rook(  'r', 0, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Rook(  'r', 7, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Knight('n', 1, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Knight('n', 6, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Bishop('b', 2, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Bishop('b', 5, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Queen( 'q', 3, 0, Player.PLAYER_B, image_size))
        black_pieces.append(King(  'k', 4, 0, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 0, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 1, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 2, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 3, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 4, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 5, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 6, 1, Player.PLAYER_B, image_size))
        black_pieces.append(Pawn(  'p', 7, 1, Player.PLAYER_B, image_size))

        self.pieces: list[Piece] = white_pieces + black_pieces
        self.createBoard()
        
        print(self.__repr__())

    def translateActionRepr(self, actionRepr: tuple) -> tuple:
        """
        Takes an action-representation tuple and reverts it to row and column
        numbers.
        Returns a tuple with original starting and target position.
        Depends on current board flip!
        """
        from_col = self.alpha_identifiers.index(actionRepr[0])
        from_row = self.numbers_identifiers.index(actionRepr[1])
        to_col = self.alpha_identifiers.index(actionRepr[3])
        to_row = self.numbers_identifiers.index(actionRepr[4])
        
        return (from_col, from_row, to_col, to_row)
    
    def printAction(self, actionLogIndex: int = -1, action: str = '', color: str = '32') -> None:
        """
        Print the last action taken ANSI-colored to the console.
        """
        print("\x1b[" + color + "m", end='')
        print(''.join(self.action_log[actionLogIndex]), action, end=' ')
        print("\x1b[m")

    def writeActionLog(self, from_col: int, from_row: int, to_col: int, to_row: int) -> None:
        """
        Take the column and row of start- and target position of any action.
        Creates a tuple representation of said action. e.g.:(C1-G5)
        Save the action taken to the action_log list. Usefull for later analysis, undo
        functionality and EnPassant attacks.
        """
        actionRepr = (self.alpha_identifiers[from_col], self.numbers_identifiers[from_row], \
            '-', self.alpha_identifiers[to_col], self.numbers_identifiers[to_row])
        self.action_log.append(actionRepr)

    def currentPlayer(self) -> str:
        """
        returns 'white' or 'black'.
        """
        return Player.OPTIONS[self.player_turn]

    def getPiece(self, col: int, row: int) -> Piece:
        """
        Takes x,y (col,row) coordinates andd returns
        the corresponding piece standing on that position.
        """
        for piece in self.pieces:
            if piece.cell_col == col and piece.cell_row == row:
                return piece
        return None

    def selectablePiece(self, piece: Piece) -> bool:
        """
        Returns a boolean, whether or not the selected Piece
        belongs no the current team-color.
        """
        return piece._player == self.currentPlayer()

    def isEmptyCell(self, col: int, row: int) -> bool:
        return not self.getPiece(col, row)

    def promotePiece(self, piece: Piece, newPieceName: str) -> None:
        """
        Takes an existing Piece and promotes it to another Piece-Type
        corresponding to the given 'newPieceName' identifier.
        (e.g. promotePiece(Pawn(...), 'q') replaces the Pawn with a new Queen)
        This should only happen to Pawn-pieces, checks havee to be made beforehand.
        """
        if newPieceName == 'r':
            promotedPiece = Rook(
                'r', piece.cell_col, piece.cell_row, piece._player, self.image_size)
        elif newPieceName == 'n':
            promotedPiece = Knight(
                'n', piece.cell_col, piece.cell_row, piece._player, self.image_size)
        elif newPieceName == 'b':
            promotedPiece = Bishop(
                'b', piece.cell_col, piece.cell_row, piece._player, self.image_size)
        else:
            promotedPiece = Queen(
                'q', piece.cell_col, piece.cell_row, piece._player, self.image_size)
        self.pieces.append(promotedPiece)
        self.pieces.remove(piece)

    def promotePawnOption(self, piece: Piece) -> bool:
        """
        Checks whether or not a piece can be promoted.
        It has to be a pawn and it has to have reached the top
        of the board.
        """
        promotable = piece._name == 'p' and \
                    (piece.cell_row == 0 or piece.cell_row == DIMENSION[1]-1)
        return promotable

    def move(self, piece: Piece, to_col: int, to_row: int, options_move: list) -> bool:
        """
            moves a 'piece' to the new coordinates 'to_col','to_row'
            if it is a valid move. Also checks for castling.
            Returns True if the move is valid and has been taken.
        """
        if not self.isEmptyCell(to_col, to_row):
            return False
        if not (to_col, to_row) in options_move:
            return False
        self.writeActionLog(piece.cell_col, piece.cell_row, to_col, to_row)
        castleOptions = self.getCastleOptions(piece)
        for castleOption, rookPosition, rook in castleOptions:
            if castleOption == (to_col, to_row):
                rook.move(rookPosition[0], rookPosition[1])
                self.printAction(-1, 'castles')
                break
        else:
            self.printAction(-1, 'moves')

        piece.move(to_col, to_row)
        return True

    def attack(self, piece: Piece, to_col: int, to_row: int, options_attack: list) -> bool:
        """
            'piece' attacks another piece at the coordinates 'to_col','to_row'
            if it is a valid attack. 
            Returns True if the attack is valid and has been taken.
        """
        enPassant = (self.getEnPassantOptions(piece) == [(to_col, to_row)])
        if self.isEmptyCell(to_col, to_row) and not enPassant:
            return False
        if not (to_col, to_row) in options_attack:
            return False
        self.writeActionLog(piece.cell_col, piece.cell_row, to_col, to_row)
        attacked_piece = self.getPiece(to_col, to_row)
        if enPassant:
            attacked_piece = self.getPiece(to_col, to_row - (1 if self.flippedAction() else -1))
        attacked_piece.health -= piece.damage
        if attacked_piece.health <= 0:
            self.printAction(-1, 'takes')
            piece.move(to_col, to_row)
            self.pieces.remove(attacked_piece)
            print("Dead:", attacked_piece)
            if attacked_piece._player == Player.PLAYER_W:
                self.white_casualties.append(attacked_piece)
            else:
                self.black_casualties.append(attacked_piece)
        else:
            self.printAction(-1, 'attacks')
        return True

    def action(self, piece: Piece, to_col: int, to_row: int, options_move: list, options_attack: list) -> bool:
        moves = self.move(piece, to_col, to_row, options_move)
        attacks = self.attack(piece, to_col, to_row, options_attack)
        return moves or attacks
    
    def playerWon(self) -> str:
        """
        Checks if a player has won, by successfully defeating the
        enemy king.
        Returns 'white' or 'black' according to the team that won,
        or returns an empty string no team has won yet.
        """
        currentEnemyPlayer = Player.OPTIONS[not self.player_turn]
        for piece in self.pieces:
            if piece._player == currentEnemyPlayer and piece._name == 'k':
                return ''
        return self.currentPlayer()

    def getOptions(self, piece: Piece) -> tuple:
        """
        Returns a tuple of lists containing all valid moves
        and attacks of a given 'piece'.
        """
        if not piece:
            return ([], [])
        options_move, options_attack = piece.getOptions(self.board, self.flippedAction())
        options_attack.extend(self.getEnPassantOptions(piece))
        castleOptions = self.getCastleOptions(piece)
        for castleOption, _, _ in castleOptions:
            options_move.append(castleOption)

        return (options_move, options_attack)

    def getCastleOptions(self, piece: Piece) -> list:
        """
        Takes a 'piece' and checks if it has
        the option to castle.
        If so the function returns a list containing tuples.
        Each tuple contains the target-position for the king to castle,
        the target-position for the rook, aswell as the rook itself.
        """
        options = []
        # current piece must be king
        if piece._name != 'k' or not piece.firstMove:
            return options
        # left castle demands rook at left-most position
        if abs(self.board[piece.cell_row, 0]) == pieceTranslateDic['r']:
            rook = self.getPiece(0, piece.cell_row)
            # rook must never have moved
            if (rook.firstMove) and (
                (np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [4, 0, 0, 0, 6])) or (  # white left
                np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [-4, 0, 0, 0, -6])) or ( # black left (noflip)
                np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [-4, 0, 0, -6]))):       # black left (flip)
                options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
        # right castle demands rook at right-most position
        if abs(self.board[piece.cell_row, DIMENSION[1]-1]) == pieceTranslateDic['r']:
            rook = self.getPiece(DIMENSION[1]-1, piece.cell_row)
            # rook must never have moved
            if (rook.firstMove) and (
                (np.array_equal(self.board[piece.cell_row, piece.cell_col:], [6, 0, 0, 4])) or (  # white right
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, -4])) or ( # black right (noflip)
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, 0, -4]))): # black right (flip)
                options.append(((piece.cell_col+2, piece.cell_row), (piece.cell_col+1, piece.cell_row), rook))
        return options

    def getEnPassantOptions(self, piece: Piece) -> list:
        """
        Takes a 'piece' and checks if it has the option to
        en Passant attack.
        If so the function returns a list containing the position-
        tuple (x, y) representing the target cell.
        """
        options = []
        # current piece must be Pawn
        if not self.action_log or piece._name != 'p':
            return options 
        from_col, from_row, to_col, to_row = self.translateActionRepr(self.action_log[-1])
        # last move must be 2-square move forward
        if abs(from_row - to_row) != 2 or (from_col - to_col) != 0:
            return options 
        # last Piece must be enemy Pawn
        if self.board[piece.cell_row, piece.cell_col] == -self.board[to_row, to_col]:
            # enemy pawn at correct position
            if (to_col, to_row) == (piece.cell_col-1, piece.cell_row) or \
                (to_col, to_row) == (piece.cell_col+1, piece.cell_row):
                options.append((to_col, to_row + (1 if self.flippedAction() else -1)))
        return options

    def flippedAction(self) -> bool:
        """
        Some actions are upside down if the current player is black
        and the board is not flipped.
        e.g.: Pawn moves/attacks + enPassant
        """
        return not (self.flip_board or self.player_turn)

    def isBoardFlipped(self) -> bool:
        return self.board_flipped

    def flipBoard(self) -> None:
        """
        flips the gameboard, by mirroring the
        x,y coordinates of all pieces at the center
        of the board.
        """
        if not self.flip_board:
            return
        self.board_flipped = not self.board_flipped
        self.alpha_identifiers.reverse()
        self.numbers_identifiers.reverse()
        for piece in self.pieces:
            piece.cell_col = flipDic[piece.cell_col]
            piece.cell_row = flipDic[piece.cell_row]

    def createBoard(self) -> None:
        """
        Creates the gameboard as a numpy.ndarray representation.
        Each piece has a unique number identifier stored in 'pieceTranslateDic'.
        e.g.: startingPosition:
        [[-4. -3. -2. -5. -6. -2. -3. -4.]       
        [-1. -1. -1. -1. -1. -1. -1. -1.]       
        [ 0.  0.  0.  0.  0.  0.  0.  0.]       
        [ 0.  0.  0.  0.  0.  0.  0.  0.]       
        [ 0.  0.  0.  0.  0.  0.  0.  0.]       
        [ 0.  0.  0.  0.  0.  0.  0.  0.]       
        [ 1.  1.  1.  1.  1.  1.  1.  1.]       
        [ 4.  3.  2.  5.  6.  2.  3.  4.]]
        """
        self.board = np.zeros(DIMENSION)
        for piece in self.pieces:
            self.board[piece.cell_row, piece.cell_col] = pieceTranslateDic[piece._name] * (
                1 if piece._player == "white" else -1
            )

    def nextTurn(self):
        """
        flips the board at switches to thee team whose
        turn it is at the moment.
        """
        self.player_turn = not self.player_turn
        self.flipBoard()
        self.createBoard()
        print(self.__repr__())

    def __str__(self) -> str:
        return self.board.__str__()

    def __repr__(self) -> str:
        return self.__str__()
