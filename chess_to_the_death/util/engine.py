import numpy as np
import chess_to_the_death.util.config as config
import chess_to_the_death.parser.argparser as argparser
from chess_to_the_death.entity.pieces import *
from chess_to_the_death.entity.player import Player
from chess_to_the_death.util.action import Action, ActionLog


DIMENSION = config.DIMENSION
pieceTranslateDic = {'p': 1, 'b': 2, 'n': 3, 'r': 4, 'q': 5, 'k': 6,
                     1: 'p', 2: 'b', 3: 'n', 4: 'r', 5: 'q', 6: 'k'}


def createPiece(name: str, col: int, row: int, player: str, image_size):
    if name == 'p':
        return Pawn(  name, col, row, player, image_size)
    if name == 'b':
        return Bishop(name, col, row, player, image_size)
    if name == 'n':
        return Knight(name, col, row, player, image_size)
    if name == 'r':
        return Rook(  name, col, row, player, image_size)
    if name == 'q':
        return Queen( name, col, row, player, image_size)
    if name == 'k':
        return King(  name, col, row, player, image_size)
    return None


class GameState:
    def __init__(self, image_size: tuple):
        self.alpha_identifiers = list(map(chr, range(65, 65+DIMENSION[1])))
        self.numbers_identifiers = list(map(str, range(DIMENSION[0], 0, -1)))
        
        self.image_size: tuple = image_size
        self.flip_board: bool = argparser.FLIP_BOARD
        self.default: bool = argparser.DEFAULT_MODE
        self.player_turn: bool = True # True -> 'white', False -> 'black'
        self.board_flipped: bool = False
        
        self.board: np.ndarray = None
        
        self.white_pieces: list[Piece] = []
        self.black_pieces: list[Piece] = []
        self.king_pieces: list[Piece] = [None, None]
        self.pieces: list[Piece] = []  
        
        self.white_casualties: list[Piece] = []
        self.black_casualties: list[Piece] = []
        
        self.action_log: ActionLog = ActionLog()
        
        self.health_damage_dict = {}

        for row in range(config.board.shape[0]):
            for col in range(config.board.shape[1]):
                if config.board[row, col] == 0:
                    continue
                pieceChar = pieceTranslateDic[abs(config.board[row, col])]
                if config.board[row, col] < 0:
                    piece = createPiece(pieceChar, col, row, Player.PLAYER_B, image_size)
                    self.black_pieces.append(piece)
                else:
                    piece = createPiece(pieceChar, col, row, Player.PLAYER_W, image_size)
                    self.white_pieces.append(piece)
                if pieceChar == 'k':
                    self.king_pieces[config.board[row, col] > 0] = piece
        
        self.pieces: list[Piece] = self.white_pieces + self.black_pieces
        if argparser.RANDOM_VALUES:
            from random import randint
            for piece in self.pieces:
                if piece._name not in self.health_damage_dict:
                    self.health_damage_dict[piece._name] = (randint(10, 150), randint(10, 150))
                piece.maxHealth = piece.health = self.health_damage_dict[piece._name][0]
                piece.damage = self.health_damage_dict[piece._name][1]
        if self.default:
            for piece in self.pieces:
                piece.maxHealth = piece.health = 1
                piece.damage = 1
        
        self.createBoard()
        print(self.__repr__())

    def translateActionRepr(self, actionRepr: Action) -> tuple:
        """
        Takes an action-object and reverts it to row and column
        numbers.
        Returns a tuple with original starting and target position.
        Depends on current board flip!
        """
        from_col = self.alpha_identifiers.index(actionRepr.from_col)
        from_row = self.numbers_identifiers.index(actionRepr.from_row)
        to_col = self.alpha_identifiers.index(actionRepr.to_col)
        to_row = self.numbers_identifiers.index(actionRepr.to_row)
        
        return (from_col, from_row, to_col, to_row)

    def writeActionLog(self, from_col: int, from_row: int, to_col: int, to_row: int, action: str = '') -> None:
        """
        Take the column and row of start- and target position of any action.
        Saves an action object of said action. e.g.:(C1-G5) to the action_log list.
        Usefull for later analysis, undo functionality and EnPassant attacks.
        """
        self.action_log.add(self.board, self.alpha_identifiers[from_col], self.numbers_identifiers[from_row],
                self.alpha_identifiers[to_col], self.numbers_identifiers[to_row], action)

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
    
    def isCellAttacked(self, col: int, row: int):
        cellTuple = (col, row)
        for piece in self.pieces:
            if piece._player == self.currentPlayer():
                continue
            options_move, options_attack = piece.getOptions(self.board, not self.flippedAction())
            if cellTuple in (options_move + options_attack):
                return True
        return False

    def promotePiece(self, piece: Piece, newPieceName: str) -> None:
        """
        Takes an existing Piece and promotes it to another Piece-Type
        corresponding to the given 'newPieceName' identifier.
        (e.g. promotePiece(Pawn(...), 'q') replaces the Pawn with a new Queen)
        This should only happen to Pawn-pieces, checks havee to be made beforehand.
        """
        promotedPiece = createPiece(newPieceName, piece.cell_col, piece.cell_row, piece._player, self.image_size)
        if argparser.RANDOM_VALUES:
            promotedPiece.maxHealth = promotedPiece.health = self.health_damage_dict[promotedPiece._name][0]
            promotedPiece.damage = self.health_damage_dict[promotedPiece._name][1]           
        if self.default:
            promotedPiece.maxHealth = promotedPiece.health = 1
            promotedPiece.damage = 1
        self.pieces.append(promotedPiece)
        if promotedPiece._player == Player.PLAYER_W:
            self.white_pieces.append(promotedPiece)
        else:
            self.black_pieces.append(promotedPiece)
        self.pieces.remove(piece)
        self.createBoard()

    def promotePawnOption(self, piece: Piece) -> bool:
        """
        Checks whether or not a piece can be promoted.
        It has to be a pawn and it has to have reached the top
        of the board.
        """
        promotable = piece._name == 'p' and \
                    (piece.cell_row == 0 or piece.cell_row == DIMENSION[1]-1)
        return promotable

    def move(self, piece: Piece, to_col: int, to_row: int, options_move: list) -> str:
        """
        moves a 'piece' to the new coordinates 'to_col','to_row'
        if it is a valid move. Also checks for castling.
        Returns an action string describing the action performed.
        """
        action = ''
        if not self.isEmptyCell(to_col, to_row):
            return action
        if not (to_col, to_row) in options_move:
            return action
        action = 'moves'
        castleOptions = self.getCastleOptions(piece)
        for castleOption, rookPosition, rook in castleOptions:
            if castleOption == (to_col, to_row):
                rook.move(rookPosition[0], rookPosition[1])
                action = 'castles'
                break

        piece.move(to_col, to_row)
        return action

    def attack(self, piece: Piece, to_col: int, to_row: int, options_attack: list) -> str:
        """
        'piece' attacks another piece at the coordinates 'to_col','to_row'
        if it is a valid attack. 
        Returns an action string describing the action performed.
        """
        action = ''
        enPassant = (self.getEnPassantOptions(piece) == [(to_col, to_row)])
        if self.isEmptyCell(to_col, to_row) and not enPassant:
            return action
        if not (to_col, to_row) in options_attack:
            return action
        action = 'attacks'
        attacked_piece = self.getPiece(to_col, to_row)
        if enPassant:
            attacked_piece = self.getPiece(to_col, to_row - (1 if self.flippedAction() else -1))
        attacked_piece.health -= piece.damage
        if attacked_piece.health <= 0:
            action = 'takes'
            piece.move(to_col, to_row)
            self.pieces.remove(attacked_piece)
            print("Dead:", attacked_piece)
            if attacked_piece._player == Player.PLAYER_W:
                self.white_pieces.remove(attacked_piece)
                self.white_casualties.append(attacked_piece)
            else:
                self.black_pieces.remove(attacked_piece)
                self.black_casualties.append(attacked_piece)

        return action

    def action(self, piece: Piece, to_col: int, to_row: int, options_move: list, options_attack: list) -> bool:
        from_cell = (piece.cell_col, piece.cell_row)
        moves = self.move(piece, to_col, to_row, options_move)
        attacks = self.attack(piece, to_col, to_row, options_attack)
        self.createBoard()
        if moves or attacks:
            self.writeActionLog(*from_cell, to_col, to_row, moves + attacks)
            self.action_log.printAction(-1)
            return True
        return False
    
    def playerWonDefault(self) -> str:
        """
        Check for default Checkmate.
        """
        won = ''
        self.player_turn = not self.player_turn
        enemyKing = self.king_pieces[self.player_turn]
        options_move, options_attack = self.checkPinnedOptions(enemyKing, *enemyKing.getOptions(self.board))
        if not (options_move + options_attack):
            for piece in self.pieces:
                if piece._player != self.currentPlayer():
                    continue
                options_move, options_attack = self.checkPinnedOptions(piece, *piece.getOptions(self.board, self.flippedAction()))
                if (options_move + options_attack):
                    break
            else:
                won = "STALEMATE!"
                if self.isCellAttacked(enemyKing.cell_col, enemyKing.cell_row):
                    won = (Player.OPTIONS[not self.player_turn] + " WON!")
                
        
        self.player_turn = not self.player_turn
        return won
    
    def gameIsDraw(self):
        draw = ''
        #by repitition
        if np.all(self.action_log.boards[-1] == self.action_log.boards, axis=(-1,1)).sum() == 3:
            draw = 'DRAW (BY REPITITION)'
            
        #insufficient material
        if len(self.pieces) <= 4:
            pieceChars = [piece._name for piece in self.pieces]
            pieceChars.sort()
            if pieceChars in [['k', 'k'], ['b', 'k', 'k'], ['k', 'k', 'n']]:
                draw = 'DRAW'
            elif pieceChars == ['b', 'b', 'k', 'k']:
                bishops = [piece for piece in self.pieces if piece._name == 'b']
                # check if bishops are on the same colored cell
                if (bishops[0].cell_col % 2 == bishops[0].cell_row % 2) == \
                    (bishops[1].cell_col % 2 == bishops[1].cell_row % 2):
                        draw = 'DRAW'
        
        return draw
    
    def playerWon(self) -> str:
        """
        Checks if a player has won, by successfully defeating the
        enemy king.
        Returns 'white' or 'black' according to the team that won,
        or returns an empty string if no team has won yet.
        """
        if self.default:
            return self.playerWonDefault() + self.gameIsDraw()
        return (self.currentPlayer() + " WON!") if (self.king_pieces[not self.player_turn].health <= 0) else ''

    def checkPinnedOptions(self, piece: Piece, options_move: list, options_attack: list) -> tuple:
        backup_values = (piece.cell_col, piece.cell_row, self.board[piece.cell_row, piece.cell_col])
        self.board[piece.cell_row, piece.cell_col] = 0
        for i in range(len(options_move)-1, -1, -1):
            self.board[options_move[i][1],options_move[i][0]] = backup_values[2]
            piece.cell_col, piece.cell_row = options_move[i][0], options_move[i][1]
            if self.isCellAttacked(self.king_pieces[self.player_turn].cell_col, self.king_pieces[self.player_turn].cell_row):
                self.board[options_move[i][1],options_move[i][0]] = 0
                del options_move[i]
                continue
            self.board[options_move[i][1],options_move[i][0]] = 0
        for i in range(len(options_attack)-1, -1, -1):
            prev_value = self.board[options_attack[i][1],options_attack[i][0]]
            self.board[options_attack[i][1],options_attack[i][0]] = backup_values[2]
            piece.cell_col, piece.cell_row = options_attack[i][0], options_attack[i][1]
            if self.isCellAttacked(self.king_pieces[self.player_turn].cell_col, self.king_pieces[self.player_turn].cell_row):
                self.board[options_attack[i][1],options_attack[i][0]] = prev_value
                del options_attack[i]
                continue
            self.board[options_attack[i][1],options_attack[i][0]] = prev_value
        piece.cell_col, piece.cell_row = backup_values[0], backup_values[1]
        self.createBoard()
        return (options_move, options_attack)

    def getOptions(self, piece: Piece) -> tuple:
        """
        Returns a tuple of lists containing all valid moves
        and attacks of a given 'piece'.
        """
        if not piece:
            return ([], [])
        options_move, options_attack = piece.getOptions(self.board, self.flippedAction())
        if self.default:
            options_move, options_attack = self.checkPinnedOptions(piece, options_move, options_attack)
            
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
                if self.default:
                    for x in range(0, piece.cell_col+1):
                        if self.isCellAttacked(x, piece.cell_row):
                            break
                    else:
                        options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
                else:
                    options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
        # right castle demands rook at right-most position
        if abs(self.board[piece.cell_row, DIMENSION[1]-1]) == pieceTranslateDic['r']:
            rook = self.getPiece(DIMENSION[1]-1, piece.cell_row)
            # rook must never have moved
            if (rook.firstMove) and (
                (np.array_equal(self.board[piece.cell_row, piece.cell_col:], [6, 0, 0, 4])) or (  # white right
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, -4])) or ( # black right (noflip)
                np.array_equal(self.board[piece.cell_row, piece.cell_col:], [-6, 0, 0, 0, -4]))): # black right (flip)
                if self.default:
                    for x in range(piece.cell_col, DIMENSION[0]):
                        if self.isCellAttacked(x, piece.cell_row):
                            break
                    else:
                        options.append(((piece.cell_col+2, piece.cell_row), (piece.cell_col+1, piece.cell_row), rook))
                else:           
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
        if not self.action_log.actions or piece._name != 'p':
            return options 
        from_col, from_row, to_col, to_row = self.translateActionRepr(self.action_log.get(-1))
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
        and the board is not flipped or if the current player is white
        and the board is flipped.
        e.g.: Pawn moves/attacks + enPassant + checkmate checking
        """
        return self.board_flipped == self.player_turn

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
            piece.cell_col = DIMENSION[1] - piece.cell_col - 1
            piece.cell_row = DIMENSION[0] - piece.cell_row - 1

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
        self.board = np.zeros(DIMENSION, dtype=np.int8)
        for piece in self.pieces:
            self.board[piece.cell_row, piece.cell_col] = pieceTranslateDic[piece._name] * (
                1 if piece._player == Player.PLAYER_W else -1
            )

    def nextTurn(self):
        """
        flips the board at switches to thee team whose
        turn it is at the moment.
        """
        self.player_turn = not self.player_turn
        self.flipBoard()
        self.createBoard()
        print(self)

    def __str__(self) -> str:
        return self.board.__str__()

    def __repr__(self) -> str:
        return self.__str__()
