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
    board: np.ndarray = None
    white_casualties, black_casualties = [], []

    def __init__(self, image_size):
        self.image_size = image_size
        
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
        return piece._name == 'p' and piece.cell_row == 0

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
        leftCastle, rook = self.getCastleOptionLeft(piece)
        if leftCastle == (to_col, to_row):
            rook.move(to_col+1, to_row)
        rightCastle, rook = self.getCastleOptionRight(piece)
        if rightCastle == (to_col, to_row):
            rook.move(to_col-1, to_row)
        piece.move(to_col, to_row)
        return True

    def attack(self, piece: Piece, to_col: int, to_row: int, options_attack: list) -> bool:
        """
            'piece' attacks another piece at the coordinates 'to_col','to_row'
            if it is a valid attack. 
            Returns True if the attack is valid and has been taken.
        """
        if self.isEmptyCell(to_col, to_row):
            return False
        if not (to_col, to_row) in options_attack:
            return False
        attacked_piece = self.getPiece(to_col, to_row)
        attacked_piece.health -= piece.damage
        if attacked_piece.health <= 0:
            piece.move(attacked_piece.cell_col, attacked_piece.cell_row)
            self.pieces.remove(attacked_piece)
            print("Dead:", attacked_piece)
            if attacked_piece._player == Player.PLAYER_W:
                self.white_casualties.append(attacked_piece)
            else:
                self.black_casualties.append(attacked_piece)
        return True

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
        options_move, options_attack = piece.getOptions(self.board)
        leftCastle, _ = self.getCastleOptionLeft(piece)
        rightCastle, _ = self.getCastleOptionRight(piece)
        if leftCastle:
            options_move.append(leftCastle)
        if rightCastle:
            options_move.append(rightCastle)

        return (options_move, options_attack)

    def getCastleOptionLeft(self, piece: Piece) -> tuple:
        """
        Takes a 'piece' and checks if it has
        the option to castle of the left side.
        If so the function returns a tuple containing the position
        to which the piece can castle, aswell as the rook included
        in the move.
        """
        if piece._name != 'k' or not piece.firstMove:
            return (None, None)
        if (self.board[piece.cell_row, piece.cell_col-1] != 0) or (
                self.board[piece.cell_row, piece.cell_col-2] != 0):
            return (None, None)
        if (self.currentPlayer() == Player.PLAYER_W):
            if (self.board[piece.cell_row, piece.cell_col-3] != 0):
                return (None, None)
            if (self.board[piece.cell_row, piece.cell_col-4] == pieceTranslateDic['r']) and (
                    self.getPiece(piece.cell_col-4, piece.cell_row).firstMove):
                return ((piece.cell_col-2, piece.cell_row), self.getPiece(piece.cell_col-4, piece.cell_row))
        if (self.currentPlayer() == Player.PLAYER_B):
            if (self.board[piece.cell_row, piece.cell_col-3] == -pieceTranslateDic['r']) and (
                    self.getPiece(piece.cell_col-3, piece.cell_row).firstMove):
                return ((piece.cell_col-2, piece.cell_row), self.getPiece(piece.cell_col-3, piece.cell_row))
        return (None, None)

    def getCastleOptionRight(self, piece: Piece):
        """
        Takes a 'piece' and checks if it has
        the option to castle of the right side.
        If so the function returns a tuple containing the position
        to which the piece can castle, aswell as the rook included
        in the move.
        """
        if piece._name != 'k' or not piece.firstMove:
            return (None, None)
        if (self.board[piece.cell_row, piece.cell_col+1] != 0) or (
                self.board[piece.cell_row, piece.cell_col+1] != 0):
            return (None, None)
        if (self.currentPlayer() == Player.PLAYER_W):
            if (self.board[piece.cell_row, piece.cell_col+3] == pieceTranslateDic['r']) and (
                    self.getPiece(piece.cell_col+3, piece.cell_row).firstMove):
                return ((piece.cell_col+2, piece.cell_row), self.getPiece(piece.cell_col+3, piece.cell_row))
        if (self.currentPlayer() == Player.PLAYER_B):
            if (self.board[piece.cell_row, piece.cell_col+3] != 0):
                return (None, None)
            if (self.board[piece.cell_row, piece.cell_col+4] == -pieceTranslateDic['r']) and (
                    self.getPiece(piece.cell_col+4, piece.cell_row).firstMove):
                return ((piece.cell_col+2, piece.cell_row), self.getPiece(piece.cell_col+4, piece.cell_row))
        return (None, None)

    def flipBoard(self) -> None:
        """
        flips the gameboard, by mirroring the
        x,y coordinates of all pieces at the center
        of the board.
        """
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
