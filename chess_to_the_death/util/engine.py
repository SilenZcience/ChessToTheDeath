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
        castleOptions = self.getCastleOptions(piece)
        for castleOption, rookPosition, rook in castleOptions:
            if castleOption == (to_col, to_row):
                rook.move(rookPosition[0], rookPosition[1])

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
        options_move, options_attack = piece.getOptions(self.board, self.flip_board or self.player_turn)
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
        if piece._name != 'k' or not piece.firstMove:
            return options
        print(self.board[piece.cell_row])
        print(self.board[piece.cell_row, :piece.cell_col+1])
        print(self.board[piece.cell_row, piece.cell_col:])
        if abs(self.board[piece.cell_row, 0]) == pieceTranslateDic['r']:
            rook = self.getPiece(0, piece.cell_row)
            if (rook.firstMove) and (
                (np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [4, 0, 0, 0, 6])) or (  # white left
                np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [-4, 0, 0, 0, -6])) or ( # black left (noflip)
                np.array_equal(self.board[piece.cell_row, :piece.cell_col+1], [-4, 0, 0, -6]))):       # black left (flip)
                options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
        if abs(self.board[piece.cell_row, DIMENSION[1]-1]) == pieceTranslateDic['r']:
            rook = self.getPiece(DIMENSION[1]-1, piece.cell_row)
            if (rook.firstMove) and (
                (np.array_equal(self.board[piece.cell_row, piece.cell_col:], [6, 0, 0, 4])) or (  # white right
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, -4])) or ( # black right (noflip)
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, 0, -4]))): # black right (flip)
                options.append(((piece.cell_col+2, piece.cell_row), (piece.cell_col+1, piece.cell_row), rook))
        return options

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
