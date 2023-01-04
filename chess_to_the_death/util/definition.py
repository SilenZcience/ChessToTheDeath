
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