import numpy as np
from chess_to_the_death.util.pieces import *
from chess_to_the_death.util.player import Player


def bothWayDic(dic):
    dic.update(dict(map(reversed, dic.items())))
    return dic


DIMENSION = (8, 8)
flipDic = bothWayDic({0: 7, 1: 6, 2: 5, 3: 4})
pieceTranslateDic = bothWayDic({'p': 1, 'b': 2, 'n': 3, 'r': 4, 'q': 5, 'k': 6})


class GameState:
    player_turn = True
    board = None
    white_casualties, black_casualties = [], []

    def __init__(self, image_size):
        self.image_size = image_size
        print(image_size)
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

        self.pieces = white_pieces + black_pieces
        self.createBoard()
        print(self.__repr__())

    def getPiece(self, col, row):
        for piece in self.pieces:
            if piece.cell_col == col and piece.cell_row == row:
                return piece
        return None

    def selectablePiece(self, piece):
        return piece._player == Player.OPTIONS[self.player_turn]

    def isEmptyCell(self, col, row):
        return not self.getPiece(col, row)

    def promotePawn(self, piece):
        if piece._name != 'p' or piece.cell_row > 0:
            return
        promotedPiece = Queen('q', piece.cell_col, 0, piece._player, self.image_size)
        self.pieces.append(promotedPiece)
        self.pieces.remove(piece)

    def move(self, piece, to_col, to_row, options_move):
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
        self.promotePawn(piece)
        return True

    def attack(self, piece, to_col, to_row, options_attack):
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
            self.promotePawn(piece)
        return True

    def playerWon(self):
        currentEnemyPlayer = Player.OPTIONS[not self.player_turn]
        for piece in self.pieces:
            if piece._player == currentEnemyPlayer and piece._name == 'k':
                return None
        return Player.OPTIONS[self.player_turn]

    def getOptions(self, piece):
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

    def getCastleOptionLeft(self, piece):
        if piece._name != 'k' or not piece.firstMove:
            return (None, None)
        if (self.board[piece.cell_row, piece.cell_col-1] != 0) or (
            self.board[piece.cell_row, piece.cell_col-2] != 0):
            return (None, None)
        if (Player.OPTIONS[self.player_turn] == Player.PLAYER_W):
            if (self.board[piece.cell_row, piece.cell_col-3] != 0):
                return (None, None)
            if (self.board[piece.cell_row, piece.cell_col-4] == pieceTranslateDic['r']) and (
                self.getPiece(piece.cell_col-4, piece.cell_row).firstMove):
                return ((piece.cell_col-2, piece.cell_row), self.getPiece(piece.cell_col-4, piece.cell_row))
        if (Player.OPTIONS[self.player_turn] == Player.PLAYER_B):
            if (self.board[piece.cell_row, piece.cell_col-3] == -pieceTranslateDic['r']) and (
                self.getPiece(piece.cell_col-3, piece.cell_row).firstMove):
                return ((piece.cell_col-2, piece.cell_row), self.getPiece(piece.cell_col-3, piece.cell_row))
        return (None, None)
    
    def getCastleOptionRight(self, piece):
        if piece._name != 'k' or not piece.firstMove:
            return (None, None)
        if (self.board[piece.cell_row, piece.cell_col+1] != 0) or (
            self.board[piece.cell_row, piece.cell_col+1] != 0):
            return (None, None)
        if (Player.OPTIONS[self.player_turn] == Player.PLAYER_W):
            if (self.board[piece.cell_row, piece.cell_col+3] == pieceTranslateDic['r']) and (
                self.getPiece(piece.cell_col+3, piece.cell_row).firstMove):
                return ((piece.cell_col+2, piece.cell_row), self.getPiece(piece.cell_col+3, piece.cell_row))
        if (Player.OPTIONS[self.player_turn] == Player.PLAYER_B):
            if (self.board[piece.cell_row, piece.cell_col+3] != 0):
                return (None, None)
            if (self.board[piece.cell_row, piece.cell_col+4] == -pieceTranslateDic['r']) and (
                self.getPiece(piece.cell_col+4, piece.cell_row).firstMove):
                return ((piece.cell_col+2, piece.cell_row), self.getPiece(piece.cell_col+4, piece.cell_row))
        return (None, None)

    def flipBoard(self):
        for piece in self.pieces:
            piece.cell_col = flipDic[piece.cell_col]
            piece.cell_row = flipDic[piece.cell_row]

    def createBoard(self):
        self.board = np.zeros(DIMENSION)
        for piece in self.pieces:
            self.board[piece.cell_row, piece.cell_col] = pieceTranslateDic[piece._name] * (
                1 if piece._player == "white" else -1
            )

    def nextTurn(self):
        self.player_turn = not self.player_turn
        self.flipBoard()
        self.createBoard()
        print(self.__repr__())

    def __str__(self):
        return self.board.__str__()

    def __repr__(self):
        return self.__str__()
