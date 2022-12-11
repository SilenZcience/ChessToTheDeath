from chess_to_the_death.util.pieces import *
from chess_to_the_death.util.player import Player

DIMENSION = (8, 8)

class GameState:
    def __init__(self):
        self.white_pieces = []
        self.white_pieces.append(Rook('r', 0, 0, Player.PLAYER_W))
        self.white_pieces.append(Rook('r', 7, 0, Player.PLAYER_W))
        self.white_pieces.append(Knight('n', 1, 0, Player.PLAYER_W))
        self.white_pieces.append(Knight('n', 6, 0, Player.PLAYER_W))
        self.white_pieces.append(Bishop('b', 2, 0, Player.PLAYER_W))
        self.white_pieces.append(Bishop('b', 5, 0, Player.PLAYER_W))
        self.white_pieces.append(Queen('q', 4, 0, Player.PLAYER_W))
        self.white_pieces.append(King('k', 3, 0, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 0, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 1, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 2, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 3, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 4, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 5, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 6, 1, Player.PLAYER_W))
        self.white_pieces.append(Pawn('p', 7, 1, Player.PLAYER_W))

        self.black_pieces = []
        self.black_pieces.append(Rook('r', 0, 7, Player.PLAYER_B))
        self.black_pieces.append(Rook('r', 7, 7, Player.PLAYER_B))
        self.black_pieces.append(Knight('n', 1, 7, Player.PLAYER_B))
        self.black_pieces.append(Knight('n', 6, 7, Player.PLAYER_B))
        self.black_pieces.append(Bishop('b', 2, 7, Player.PLAYER_B))
        self.black_pieces.append(Bishop('b', 5, 7, Player.PLAYER_B))
        self.black_pieces.append(Queen('q', 4, 7, Player.PLAYER_B))
        self.black_pieces.append(King('k', 3, 7, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 0, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 1, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 2, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 3, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 4, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 5, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 6, 6, Player.PLAYER_B))
        self.black_pieces.append(Pawn('p', 7, 6, Player.PLAYER_B))
        
        self.pieces = self.white_pieces + self.black_pieces

        self.board = [
            [*self.white_pieces[0:8]],
            [*self.white_pieces[8:16]],
            [Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY,
             Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY],
            [Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY,
             Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY],
            [Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY,
             Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY],
            [Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY,
             Player.EMPTY, Player.EMPTY, Player.EMPTY, Player.EMPTY],
            [*self.black_pieces[8:16]],
            [self.black_pieces[0:8]]
        ]
        
    def getPiece(self, col, row):
        if (0 <= col < 8) and (0 <= row < 8):
            return self.board[row][col]