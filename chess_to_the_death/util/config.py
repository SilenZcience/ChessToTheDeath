import numpy as np

board = np.asarray([[-4, -3, -2, -5, -6, -2, -3, -4],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 0,  0,  0,  0,  0,  0,  0,  0],
                    [ 1,  1,  1,  1,  1,  1,  1,  1],
                    [ 4,  3,  2,  5,  6,  2,  3,  4]], dtype=np.int8)

DIMENSION = board.shape
assert DIMENSION[0] == DIMENSION[1]