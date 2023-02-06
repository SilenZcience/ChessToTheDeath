
class Outcome:
    NONE = ''
    PAWN_PROMOTION = 'PAWN_PROMOTION'
    GAME_FINISHED = 'GAME_FINISHED'
    
    WHITE_WON = 'WHITE WON'
    BLACK_WON = 'BLACK WON'
    
    STALEMATE = 'STALEMATE'
    DRAW_REPITITION = 'DRAW (BY REPITITION)'
    DRAW = 'DRAW'
    
class ActionName:
    NONE = ''
    MOVES = 'moves'
    CASTLES = 'castles'
    ATTACKS = 'attacks'
    TAKES = 'takes'
    
class PieceChar:
    UNDEFINED = ''
    PAWN = 'p'
    BISHOP = 'b'
    KNIGHT = 'n'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'
    OBSTACLE = 'x'
    
class PieceNames:
    NAMES = {PieceChar.UNDEFINED: 'Undefined',
             PieceChar.PAWN: 'Pawn',
             PieceChar.BISHOP: 'Bishop',
             PieceChar.KNIGHT: 'Kight',
             PieceChar.ROOK: 'Rook',
             PieceChar.QUEEN: 'Queen',
             PieceChar.KING: 'King',
             PieceChar.OBSTACLE: 'Obstacle'}
    
class PieceValues:
    VALUES = {PieceChar.UNDEFINED: 0,
             PieceChar.PAWN: 1,
             PieceChar.BISHOP: 3,
             PieceChar.KNIGHT: 3,
             PieceChar.ROOK: 5,
             PieceChar.QUEEN: 9,
             PieceChar.KING: 10,
             PieceChar.OBSTACLE: 0}