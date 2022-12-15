from os import path
from pygame import image, transform

workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)
basePath = path.join(workingDir, 'images')
PIECE_IMAGES = {}


def loadImage(relPath, size):
    pieceName = relPath
    if not (pieceName + str(size[0]) + "x" + str(size[1])) in PIECE_IMAGES:
        PIECE_IMAGES[pieceName + str(size[0]) + "x" + str(size[1])] = transform.smoothscale(
            image.load(path.join(basePath, relPath + ".png")), size)
    return PIECE_IMAGES[pieceName + str(size[0]) + "x" + str(size[1])]
