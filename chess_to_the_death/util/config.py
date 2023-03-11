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

def generateBoardFromFEN(fen: str) -> None:
    if fen == None:
        return
    global board
    global DIMENSION
    whiteSpaceSplit = fen.split(" ")
    assert len(whiteSpaceSplit) >= 2, "The FEN representation looks something like:\nrnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    boardSplit = whiteSpaceSplit[0].split("/")
    tempBoard = []
    for i, row in enumerate(boardSplit):
        tempBoard.append([])
        for char in row:
            if char.isnumeric():
                tempBoard[i] += [0] * int(char)
            else:
                try:
                    pieceID = pieceTranslateDic[char.lower()]
                    if char.upper() != char:
                        pieceID *= -1
                    tempBoard[i].append(pieceID)
                except KeyError:
                    tempBoard[i].append(0)
    rowLenMap = map(len, tempBoard)
    maxRowLength = max(rowLenMap)
    # if the requested position has an inhomogeneous shape
    if len(set(rowLenMap)) != 1:
        tempBoard = [row + [0] * (maxRowLength-len(row)) for row in tempBoard]
    board = np.asarray(tempBoard, dtype=boardDtype)
    DIMENSION = board.shape
    assert np.count_nonzero(board == 6) == np.count_nonzero(board == -6) == 1, "There can only be one King to each color!"
