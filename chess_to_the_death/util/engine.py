import numpy as np
from itertools import product

import chess_to_the_death.util.config as config
import chess_to_the_death.parser.argparser as argparser
from chess_to_the_death.entity.pieces import *
from chess_to_the_death.entity.player import Player
from chess_to_the_death.util.action import Action, ActionLog
from chess_to_the_death.util.definition import *


def createPiece(name: str, pos: tuple, player: str, image_size):
    """
    return the Piece Object according to the char identifier 'name'
    """
    if name == PieceChar.PAWN:
        return Pawn(  pos, player, image_size)
    if name == PieceChar.BISHOP:
        return Bishop(pos, player, image_size)
    if name == PieceChar.KNIGHT:
        return Knight(pos, player, image_size)
    if name == PieceChar.ROOK:
        return Rook(  pos, player, image_size)
    if name == PieceChar.QUEEN:
        return Queen( pos, player, image_size)
    if name == PieceChar.KING:
        return King(  pos, player, image_size)
    print("Unknown Piece:", name)
    return None


def printValueStatistic(health_damage_dict: dict) -> None:
    print("-------------------- Statistics --------------------")
    pieceTypes = list(health_damage_dict.keys())
    pieceNames = [PieceNames.NAMES[pT] for pT in pieceTypes]
    health_values = [health_damage_dict[pT][0] for pT in pieceTypes]
    attack_values = [health_damage_dict[pT][1] for pT in pieceTypes]
    longestString = 1 + max(len(str(x)) for x in (pieceNames + health_values + attack_values))
    
    print("Piece :", end='')
    print(*[val.rjust(longestString) for val in pieceNames], sep='')

    print("Health:", end='')
    print(*[str(val).rjust(longestString) for val in health_values], sep='')
        
    print("Damage:", end='')
    print(*[str(val).rjust(longestString) for val in attack_values], sep='')
        
    print("\nHits to the Death:")
    
    health_values = np.array(health_values)
    attack_values = np.array(attack_values)
    hits_to_death = np.ceil(health_values.reshape(-1, 1).repeat(attack_values.shape[0], axis=1) / attack_values)
    
    print('H/D'.rjust(longestString), end='')
    print(*[val.rjust(longestString) for val in pieceNames], sep='')
    
    for y in range(hits_to_death.shape[0]):
        print(pieceNames[y].rjust(longestString), end='')
        print(*[str(int(val)).rjust(longestString) for val in list(hits_to_death[y])], sep='')
    
    
    print("----------------------------------------------------")


class GameState:
    def __init__(self, image_size: tuple):
        self.alpha_identifiers = list(map(chr, range(65, 65+config.DIMENSION[1])))
        self.numbers_identifiers = list(map(str, range(config.DIMENSION[0], 0, -1)))
        
        self.image_size: tuple = image_size
        self.flip_board: bool = argparser.FLIP_BOARD
        self.default: bool = argparser.DEFAULT_MODE
        self.random: bool = argparser.RANDOM_VALUES
        self.crazy: bool = argparser.CRAZY_MODE
        self.player_turn: bool = True # True -> 'white', False -> 'black'
        self.board_flipped: bool = False
        
        self.board: np.ndarray = None
        
        self.white_pieces: list[Piece] = []
        self.black_pieces: list[Piece] = []
        self.king_pieces: list[Piece] = [None, None]
        self.pieces: list[Piece] = []  
        
        self.white_casualties: list[Piece] = []
        self.black_casualties: list[Piece] = []
        self.white_crazyoptions: list[Piece] = []
        self.black_crazyoptions: list[Piece] = []
        self.value_taken: list[int] = [0, 0]
        
        self.action_log: ActionLog = ActionLog()
        
        self.health_damage_dict = {}

        # generate the pieces of the default gameBoard defined in config.py
        for row in range(config.board.shape[0]):
            for col in range(config.board.shape[1]):
                if config.board[row, col] == 0:
                    continue
                pieceChar = pieceTranslateDic[abs(config.board[row, col])]
                if config.board[row, col] < 0:
                    piece = createPiece(pieceChar, (col, row), Player.PLAYER_B, image_size)
                    self.black_pieces.append(piece)
                else:
                    piece = createPiece(pieceChar, (col, row), Player.PLAYER_W, image_size)
                    self.white_pieces.append(piece)
                if pieceChar == PieceChar.KING:
                    self.king_pieces[config.board[row, col] > 0] = piece
        
        self.pieces: list[Piece] = self.white_pieces + self.black_pieces
        # assign each piece type a random health- and damage value
        # save the value in health_damage_dict for possible pawn promotions
        # if the random parameter is given, otherwise save the default
        # values
        if self.random:
            from random import randint
        for piece in self.pieces:
            if piece._name not in self.health_damage_dict:
                if self.random:
                    self.health_damage_dict[piece._name] = (randint(10, 150), randint(10, 150))
                else:
                    self.health_damage_dict[piece._name] = (piece.health, piece.damage)
            piece.maxHealth = piece.health = self.health_damage_dict[piece._name][0]
            piece.damage = self.health_damage_dict[piece._name][1]

        # the default parameters actually sets all health- an damage values to 1
        # since 0 might throw division error
        if self.default:
            for piece in self.pieces:
                piece.maxHealth = piece.health = 1
                piece.damage = 1
        else:
            # if not the default variant is palyed, print the statistics
            # about piece health/damage values.
            printValueStatistic(self.health_damage_dict)
        if config.BLACKS_TURN:
            self.nextTurn(False)
        self.createBoard()
        print(self.__repr__())
        
        self.player_turn = not self.player_turn
        if (self.default and self.isCellAttacked(self.king_pieces[self.player_turn].getPos())) or \
             not (np.count_nonzero(self.board == pieceTranslateDic[PieceChar.KING]) == np.count_nonzero(self.board == -pieceTranslateDic[PieceChar.KING]) == 1):
            print('\x1b[31mCannot load position because it is invalid. Every position must have exactly one king of each color, and the side to move must not be able to capture the enemy king.\x1b[0m')
            from sys import exit as sysexit
            sysexit(1)
        currentOutcome = self.playerWon()
        if currentOutcome != Outcome.NONE:
            print('\x1b[31mCannot load position because it has already reached a finished state:\x1b[0m')
            print('\x1b[31m', currentOutcome, '\x1b[0m', sep='')
            from sys import exit as sysexit
            sysexit(1)
        self.player_turn = not self.player_turn

    def translateActionRepr(self, actionRepr: Action) -> list:
        """
        Takes an action-object and reverts it to row and column numbers.
        Returns a list with original starting and target position tuple.
        Depends on current board flip!
        """
        from_col = self.alpha_identifiers.index(actionRepr.from_col)
        from_row = self.numbers_identifiers.index(actionRepr.from_row)
        to_col = self.alpha_identifiers.index(actionRepr.to_col)
        to_row = self.numbers_identifiers.index(actionRepr.to_row)
        
        return [(from_col, from_row), (to_col, to_row)]

    def writeActionLog(self, from_pos: tuple, to_pos: tuple, action: str = '', pieceChar: str = PieceChar.UNDEFINED) -> None:
        """
        Take the column and row of start- and target position of any action.
        Saves an action object of said action. e.g.:(C1-G5) to the action_log list.
        Usefull for later analysis, undo functionality and EnPassant attacks.
        """
        pieceName = PieceNames.NAMES[pieceChar]
        if pieceName == PieceNames.NAMES[PieceChar.UNDEFINED]:
            pieceName = ''
        self.action_log.add(self.board, self.alpha_identifiers[from_pos[0]], self.numbers_identifiers[from_pos[1]],
                self.alpha_identifiers[to_pos[0]], self.numbers_identifiers[to_pos[1]], action, pieceName)
        
    def getPlayerValue(self) -> tuple:
        """
        return a tuple containing the piece-values, that have been taken.
        """
        white_casualties_ids = [p._name for p in self.white_casualties]
        black_casualties_ids = [p._name for p in self.black_casualties]
        white_casualties_ids.sort()
        black_casualties_ids.sort()
        for id in white_casualties_ids[:]:
            if id in black_casualties_ids:
                white_casualties_ids.remove(id)
                black_casualties_ids.remove(id)
        for id in black_casualties_ids[:]:
            if id in white_casualties_ids:
                white_casualties_ids.remove(id)
                black_casualties_ids.remove(id)
            
        return (self.value_taken[1] - self.value_taken[0], white_casualties_ids, black_casualties_ids)

    def getCrazyPlaceOptionsPieces(self):
        if self.currentPlayer() == Player.PLAYER_W:
            return self.black_crazyoptions
        return self.white_crazyoptions
    
    def setCrazyPlaceOptionsPieces(self, casualties: list):
        if self.currentPlayer() == Player.PLAYER_W:
            self.black_crazyoptions = casualties[:]
        else:
            self.white_crazyoptions = casualties[:]

    def currentPlayer(self) -> str:
        """
        returns 'white' or 'black'.
        """
        return Player.OPTIONS[self.player_turn]

    def getPiece(self, pos: tuple) -> Piece:
        """
        Takes a position tuple with (x,y) coordinates and returns
        the corresponding piece standing on that position.
        """
        for piece in self.pieces:
            if piece.getPos() == pos:
                return piece
        return None

    def selectablePiece(self, piece: Piece) -> bool:
        """
        Returns a boolean, whether or not the selected Piece
        belongs no the current team-color.
        """
        return piece._player == self.currentPlayer()

    def isEmptyCell(self, pos: tuple) -> bool:
        return not self.getPiece(pos)
    
    def isCellAttacked(self, pos: tuple) -> bool:
        """
        Check if a given cell is threatened by any enemy piece.
        """
        for piece in self.pieces:
            if piece._player == self.currentPlayer():
                continue
            options_move, options_attack = piece.getOptions(self.board, not self.flippedAction())
            if pos in (options_move + options_attack):
                return True
        return False

    def placePiece(self, pos: tuple, newPieceName: str) -> None:
        """
        Takes an existing Piece and promotes it to another Piece-Type
        corresponding to the given 'newPieceName' identifier.
        (e.g. placePiece(Pawn(...), 'q') replaces the Pawn with a new Queen)
        This should only happen to Pawn-pieces, checks have to be made beforehand.
        """
        oldPiece = self.getPiece(pos)
        promotedPiece = createPiece(newPieceName, pos, self.currentPlayer(), self.image_size)
        # set health- and damage values corresponding to the given argv parameters
        if self.random:
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
        if oldPiece:
            self.pieces.remove(oldPiece)
            if oldPiece._player == Player.PLAYER_W:
                self.white_pieces.remove(oldPiece)
            else:
                self.black_pieces.remove(oldPiece)
        else:
            self.writeActionLog(pos, pos, 'placed', newPieceName)
            self.action_log.printAction(-1)
        self.createBoard()

    def promotePawnOption(self, piece: Piece) -> bool:
        """
        Checks whether or not a piece can be promoted.
        It has to be a pawn and it has to have reached the top/bottom
        of the board.
        """
        promotable = piece._name == PieceChar.PAWN and \
                    piece.cell_row in [0, config.DIMENSION[0]-1]
        return promotable

    def move(self, piece: Piece, to_pos: tuple, options_move: list) -> str:
        """
        moves a 'piece' to the new coordinates of the to_pos tuple
        if it is a valid move. Also checks for castling.
        Returns an action string describing the action performed.
        """
        action = ActionName.NONE
        if not self.isEmptyCell(to_pos):
            return action
        if to_pos not in options_move:
            return action
        action = ActionName.MOVES
        castleOptions = self.getCastleOptions(piece)
        for castleOption, rookPosition, rook in castleOptions:
            if castleOption == to_pos:
                rook.move(rookPosition)
                action = ActionName.CASTLES
                break

        piece.move(to_pos)
        return action

    def attack(self, piece: Piece, to_pos: tuple, options_attack: list) -> str:
        """
        'piece' attacks another piece at the coordinates of the to_pos tuple
        if it is a valid attack. 
        Returns an action string describing the action performed.
        """
        action = ActionName.NONE
        enPassant = (self.getEnPassantOptions(piece) == [to_pos])
        if self.isEmptyCell(to_pos) and not enPassant:
            return action
        if to_pos not in options_attack:
            return action
        action = ActionName.ATTACKS
        attacked_piece = self.getPiece(to_pos)
        if enPassant:
            attacked_piece = self.getPiece((to_pos[0], to_pos[1] - (1 if self.flippedAction() else -1)))
        attacked_piece.health -= piece.damage
        if attacked_piece.health <= 0:
            action = ActionName.TAKES
            piece.move(to_pos)
            self.pieces.remove(attacked_piece)
            print("Dead:", attacked_piece)
            if attacked_piece._player == Player.PLAYER_W:
                self.white_pieces.remove(attacked_piece)
                self.white_casualties.append(attacked_piece)
                self.white_crazyoptions.append(attacked_piece)
            else:
                self.black_pieces.remove(attacked_piece)
                self.black_casualties.append(attacked_piece)
                self.black_crazyoptions.append(attacked_piece)
            self.value_taken[self.player_turn] += PieceValues.VALUES[attacked_piece._name]

        return action

    def action(self, piece: Piece, to_pos: tuple, options_move: list, options_attack: list) -> str:
        """
        Return an empty string if the action could not be performed (should generally not happen).
        Returns the action taken or in special cases an identifying string for promotion or game-end.
        """
        gameStateAction = ''
        if not piece:
            return gameStateAction
        from_pos = piece.getPos()
        moves = self.move(piece, to_pos, options_move)
        attacks = self.attack(piece, to_pos, options_attack)
        gameStateAction = moves + attacks
        self.createBoard()
        if gameStateAction:
            self.writeActionLog(from_pos, to_pos, moves + attacks)
            self.action_log.printAction(-1)
            if self.playerWon():
                return Outcome.GAME_FINISHED
            if self.promotePawnOption(piece):
                return Outcome.PAWN_PROMOTION
        return gameStateAction
    
    def playerWonDefault(self) -> str:
        """
        Check for default Checkmate and Stalemate.
        """
        outcome = Outcome.NONE
        # temporarily switch player side
        self.player_turn = not self.player_turn
        enemyKing = self.king_pieces[self.player_turn]
        options_move, options_attack = self.checkPinnedOptions(enemyKing, *enemyKing.getOptions(self.board))
        # if the king has no legal moves left
        if not (options_move + options_attack):
            # check if any other piece has a legal move left
            for piece in self.pieces:
                if piece._player != self.currentPlayer():
                    continue
                options_move, options_attack = self.checkPinnedOptions(piece, *piece.getOptions(self.board, self.flippedAction()))
                if (options_move + options_attack):
                    break
            else:
                # if not it is stalemate or, if the king is currently threatened,
                # it is checkmate
                outcome = Outcome.STALEMATE
                if self.isCellAttacked(enemyKing.getPos()):
                    if self.player_turn:
                        outcome = Outcome.BLACK_WON
                    else:
                        outcome = Outcome.WHITE_WON
                if self.crazy:
                    placementOptions = self.getCrazyPlaceOptionsPieces()
                    if placementOptions:
                        if outcome == Outcome.STALEMATE:
                            outcome = Outcome.NONE
                        else:
                            for pos in product(range(config.DIMENSION[1]), range(config.DIMENSION[0])):
                                if self.board[pos[1], pos[0]] != 0:
                                    continue
                                if self._restrictedCrazyPlaceDefault(pos):
                                    outcome = Outcome.NONE
                                    break
                        
                
        # switch back to actual player
        self.player_turn = not self.player_turn
        return outcome
    
    def gameIsDraw(self):
        outcome = Outcome.NONE
        #by repitition

        if len(self.action_log.boards) and np.all(self.action_log.boards[-1] == self.action_log.boards, axis=(-1,1)).sum() == 3:
            outcome = Outcome.DRAW_REPITITION
        
        if self.crazy:
            return outcome
        
        #insufficient material
        if len(self.pieces) <= 4:
            pieceChars = [piece._name for piece in self.pieces]
            pieceChars.sort()
            twoKings = [PieceChar.KING, PieceChar.KING]
            bishop = [PieceChar.BISHOP]
            knight = [PieceChar.KNIGHT]
            if pieceChars in [twoKings, twoKings + bishop, twoKings + knight]:
                outcome = Outcome.DRAW
            elif pieceChars == twoKings + bishop * 2:
                bishops = [piece for piece in self.pieces if piece._name == PieceChar.BISHOP]
                # check if bishops are on the same colored cell
                if (bishops[0].cell_col % 2 == bishops[0].cell_row % 2) == \
                    (bishops[1].cell_col % 2 == bishops[1].cell_row % 2):
                        outcome = Outcome.DRAW
        
        return outcome
    
    def playerWon(self) -> str:
        """
        Checks if a player has won, by successfully defeating the
        enemy king.
        Returns 'white' or 'black' according to the team that won,
        or returns an empty string if no team has won yet.
        """
        if self.default:
            gameDraw = self.gameIsDraw()
            if gameDraw:
                return gameDraw
            gameWon = self.playerWonDefault()
            return gameWon
        outcome = Outcome.NONE
        if (self.king_pieces[not self.player_turn].health <= 0):
            if self.player_turn:
                outcome = Outcome.WHITE_WON
            else:
                outcome = Outcome.BLACK_WON
        return outcome

    def _restrictedCrazyPlaceDefault(self, pos: tuple) -> bool:
        """
        check if the friendly king would be threatened even with the
        newly placed piece.
        """
        placementAllowed = False
        # temporarily block the position in question on the board
        self.board[pos[1],pos[0]] = pieceTranslateDic[PieceChar.OBSTACLE]
        # get the position of the current king
        friendlyKingPos = self.king_pieces[self.player_turn].getPos()
        
        for piece in self.pieces:
            if piece._player == self.currentPlayer():
                continue
            options_move, options_attack = piece.getOptions(self.board, not self.flippedAction())
            # if an enemy piece threatens king, the placement is not allowed
            if friendlyKingPos in (options_move + options_attack):
                break
        else:
            # if no enemy piece threatens the king, the placement is allowed
            placementAllowed = True

        # reset the position
        self.board[pos[1],pos[0]] = 0
        return placementAllowed

    def restrictedCrazyPlace(self, pos: tuple) -> bool:
        """
        check if a 'crazy' - piece placement is allowed at position 'pos'
        """
        piece = self.getPiece(pos)
        # the position has to be empty
        if piece:
            return False
        # it only matters in default mode
        if not self.default:
            return True
        return self._restrictedCrazyPlaceDefault(pos)
    
    def checkPinnedOptions(self, piece: Piece, options_move: list, options_attack: list) -> tuple:
        """
        check if a piece is pinned such that it cannot move without exposing the king to attacks.
        """
        backup_values = (piece.getPos(), self.board[piece.cell_row, piece.cell_col])
        self.board[piece.cell_row, piece.cell_col] = 0
        for i in range(len(options_move)-1, -1, -1):
            self.board[options_move[i][1],options_move[i][0]] = backup_values[1]
            piece.setPos(options_move[i])
            if self.isCellAttacked(self.king_pieces[self.player_turn].getPos()):
                self.board[options_move[i][1],options_move[i][0]] = 0
                del options_move[i]
                continue
            self.board[options_move[i][1],options_move[i][0]] = 0
        for i in range(len(options_attack)-1, -1, -1):
            prev_value = self.board[options_attack[i][1],options_attack[i][0]]
            self.board[options_attack[i][1],options_attack[i][0]] = backup_values[1]
            piece.setPos(options_attack[i])
            if self.isCellAttacked(self.king_pieces[self.player_turn].getPos()):
                self.board[options_attack[i][1],options_attack[i][0]] = prev_value
                del options_attack[i]
                continue
            self.board[options_attack[i][1],options_attack[i][0]] = prev_value
        piece.setPos(backup_values[0])
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
        Takes a 'piece' and checks if it has the option to castle.
        If so the function returns a list containing tuples.
        Each tuple contains the target-position for the king to castle,
        the target-position for the rook, aswell as the rook itself.
        """
        options = []
        # current piece must be king
        if piece._name != PieceChar.KING or not piece.firstMove:
            return options
        # left castle demands rook at left-most position
        if abs(self.board[piece.cell_row, 0]) == pieceTranslateDic[PieceChar.ROOK]:
            rook = self.getPiece((0, piece.cell_row))
            # rook must never have moved and no pieces between rook and king
            if (rook.firstMove) and (np.all(self.board[piece.cell_row, 1:piece.cell_col] == 0)):
                if self.default:
                    for x in range(0, piece.cell_col+1):
                        if self.isCellAttacked((x, piece.cell_row)):
                            break
                    else:
                        options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
                else:
                    options.append(((piece.cell_col-2, piece.cell_row), (piece.cell_col-1, piece.cell_row), rook))
        # right castle demands rook at right-most position
        if abs(self.board[piece.cell_row, config.DIMENSION[1]-1]) == pieceTranslateDic[PieceChar.ROOK]:
            rook = self.getPiece((config.DIMENSION[1]-1, piece.cell_row))
            # rook must never have moved and no pieces between rook and king
            if (rook.firstMove) and (np.all(self.board[piece.cell_row, piece.cell_col+1:config.DIMENSION[1]-1] == 0)):
                if self.default:
                    for x in range(piece.cell_col, config.DIMENSION[0]):
                        if self.isCellAttacked((x, piece.cell_row)):
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
        if not self.action_log.actions or piece._name != PieceChar.PAWN:
            return options
        last_move = self.translateActionRepr(self.action_log.get(-1))
        from_col, from_row = last_move[0]
        to_col, to_row = last_move[1]
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
            piece.cell_col = config.DIMENSION[1] - piece.cell_col - 1
            piece.cell_row = config.DIMENSION[0] - piece.cell_row - 1

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
        self.board = np.zeros(config.DIMENSION, dtype=config.boardDtype)
        for piece in self.pieces:
            self.board[piece.cell_row, piece.cell_col] = pieceTranslateDic[piece._name] * (
                1 if piece._player == Player.PLAYER_W else -1
            )

    def nextTurn(self, displayInfo = True) -> None:
        """
        flips the board and switches to the team whose
        turn it is at the moment.
        """
        self.player_turn = not self.player_turn
        self.flipBoard()
        self.createBoard()
        if not displayInfo:
            return
        print(self)
        playerValue, white_diff, black_diff = self.getPlayerValue()
        if playerValue == 0:
            return
        elif playerValue > 0:
            print('white: +', playerValue, sep='')
            if black_diff:
                print(*black_diff)
            if white_diff:
                print('black:')
                print(*white_diff)
        elif playerValue < 0:
            if black_diff:
                print('white:')
                print(*black_diff)
            print('black: +', abs(playerValue), sep='')
            if white_diff:
                print(*white_diff)
        if self.crazy:
            placableWhite = [p._name for p in self.black_crazyoptions]
            placableBlack = [p._name for p in self.white_crazyoptions]
            placableWhite.sort()
            placableBlack.sort()
            if placableWhite:
                print('placement options (white):')
                print(*placableWhite)
            if placableBlack:
                print('placement options (black):')
                print(*placableBlack)

    def __str__(self) -> str:
        boardRepr = '  '.join(self.alpha_identifiers[:config.DIMENSION[1]]) + ' |\n'
        boardRepr += '-' * (3 * config.DIMENSION[1] - 1) + '|' + '-' * len(str(config.DIMENSION[0])) + '\n'
        number_ids = [' |' + id for id in self.numbers_identifiers[:config.DIMENSION[0]]]
        board = ['  '.join(map(lambda x: "\x1b[" + "36" * (x > 0) + "31" * (x < 0) + ";1m" + pieceTranslateDic[abs(x)] + "\x1b[0m", row)) for row in self.board]
        boardRepr += '\n'.join(list(''.join(row) for row in zip(board, number_ids)))
        return boardRepr

    def __repr__(self) -> str:
        return self.__str__()
