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
assert np.count_nonzero(board == 6) == np.count_nonzero(board == -6) == 1, "There can only be one King to each color!"
