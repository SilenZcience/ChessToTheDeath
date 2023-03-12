import numpy as np
from chess_to_the_death.util.definition import pieceTranslateDic


boardDtype = np.int8
board = np.asarray([[-4, -3, -2, -5, -6, -2, -3, -4],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 1,  1,  1,  1,  1,  1,  1,  1],
                    [ 4,  3,  2,  5,  6,  2,  3,  4]], dtype=boardDtype)

DIMENSION = board.shape
assert (len(pieceTranslateDic)//2) ** 2 <= np.iinfo(boardDtype).max, "The BoardDtype has to be smaller than sqrt(max(pieceID))."
BLACKS_TURN = False

def generateBoardFromFEN(fen: str) -> None:
    if fen == None:
        return
    global board
    global DIMENSION
    global BLACKS_TURN
    whiteSpaceSplit = fen.split(" ")
    boardSplit = whiteSpaceSplit[0].split("/")
    tempBoard = []
    for i, row in enumerate(boardSplit):
        tempBoard.append([])
        empty = "0"
        for char in row:
            if char.isnumeric():
                empty += char
            else:
                tempBoard[i] += [0] * int(empty)
                empty = "0"
                try:
                    pieceID = pieceTranslateDic[char.lower()]
                    if char.upper() != char:
                        pieceID *= -1
                    tempBoard[i].append(pieceID)
                except KeyError:
                    tempBoard[i].append(0)
        tempBoard[i] += [0] * int(empty)
    rowLenMap = map(len, tempBoard)
    maxRowLength = max(rowLenMap)
    # if the requested position has an inhomogeneous shape
    if len(set(rowLenMap)) != 1:
        tempBoard = [row + [0] * (maxRowLength-len(row)) for row in tempBoard]
    board = np.asarray(tempBoard, dtype=boardDtype)
    DIMENSION = board.shape
    assert np.count_nonzero(board == 6) == np.count_nonzero(board == -6) == 1, "There can only be one King to each color!"
    if len(whiteSpaceSplit) >= 2:
        if whiteSpaceSplit[1].upper() == "B":
            BLACKS_TURN = True


def generateFENFromBoard(board: np.ndarray, whites_turn: bool) -> str:
    player_turn = "w" if whites_turn else "b"
    if not whites_turn:
        board = np.flip(board, (0,1))
    fenRows = []
    for row in board:
        fenRow = ""
        empty = 0
        for pieceID in row:
            if pieceID != 0:
                if empty > 0:
                    fenRow += str(empty)
                    empty = 0
                fenChar = pieceTranslateDic[abs(pieceID)]
                if pieceID > 0:
                    fenChar = fenChar.upper()
                fenRow += fenChar
            else:
                empty += 1
        if empty > 0:
            fenRow += str(empty)
        fenRows.append(fenRow)
    return f"{'/'.join(fenRows)} {player_turn} KQkq - 0 1"
