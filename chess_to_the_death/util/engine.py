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

    def __init__(self):
        self.white_pieces = []
        self.white_pieces.append(Rook('r', 0, 7, Player.PLAYER_W))
        self.white_pieces.append(Rook('r', 7, 7, Player.PLAYER_W))
        self.white_pieces.append(Knight('n', 1, 7, Player.PLAYER_W))
        self.white_pieces.append(Knight('n', 6, 7, Player.PLAYER_W))
        self.white_pieces.append(Bishop('b', 2, 7, Player.PLAYER_W))
        self.white_pieces.append(Bishop('b', 5, 7, Player.PLAYER_W))
        self.white_pieces.append(Queen('q', 4, 7, Player.PLAYER_W))
        self.white_pieces.append(King('k', 3, 7, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 0, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 1, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 2, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 3, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 4, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 5, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 6, 6, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 7, 6, Player.PLAYER_W))

        self.black_pieces = []
        self.black_pieces.append(Rook('r', 0, 0, Player.PLAYER_B))
        self.black_pieces.append(Rook('r', 7, 0, Player.PLAYER_B))
        self.black_pieces.append(Knight('n', 1, 0, Player.PLAYER_B))
        self.black_pieces.append(Knight('n', 6, 0, Player.PLAYER_B))
        self.black_pieces.append(Bishop('b', 2, 0, Player.PLAYER_B))
        self.black_pieces.append(Bishop('b', 5, 0, Player.PLAYER_B))
        self.black_pieces.append(Queen('q', 4, 0, Player.PLAYER_B))
        self.black_pieces.append(King('k', 3, 0, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 0, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 1, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 2, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 3, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 4, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 5, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 6, 1, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 7, 1, Player.PLAYER_B))

        self.pieces = self.white_pieces + self.black_pieces

    def getPiece(self, col, row):
        for piece in self.pieces:
            if piece.cell_x == col and piece.cell_y == row:
                return piece
        return None

    def selectablePiece(self, piece):
        return piece._player == Player.OPTIONS[self.player_turn]

    def isEmptyCell(self, col, row):
        return not self.getPiece(col, row)

    def move(self, piece, to_col, to_row):
        if not self.isEmptyCell(to_col, to_row):
            return False
        piece.cell_x = to_col
        piece.cell_y = to_row
        return True

    def flipBoard(self):
        for piece in self.pieces:
            piece.cell_x = flipDic[piece.cell_x]
            piece.cell_y = flipDic[piece.cell_y]

    def nextTurn(self):
        self.player_turn = not self.player_turn
        self.flipBoard()
    
    def createBoard(self):
        self.board = np.zeros(DIMENSION)
        for piece in self.pieces:
            self.board[piece.cell_y:piece.cell_y+1,piece.cell_x:piece.cell_x+1] = pieceTranslateDic[piece._name] * (
                1 if piece._player == "white" else -1
            )      
    
    def __str__(self):
        self.createBoard()
        return self.board.__str__()
    
    def __repr__(self):
        return self.__str__()
