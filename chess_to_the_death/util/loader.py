from os import path
from pygame import image, transform

workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)
basePath = path.join(workingDir, 'images')
PIECE_IMAGES = {}


def loadImage(relPath, size, store_value=True):
    pieceName = relPath
    if not pieceName in PIECE_IMAGES:
        _image = transform.smoothscale(image.load(path.join(basePath, relPath + ".png")),
                size)
        if store_value:
            PIECE_IMAGES[pieceName] = _image
        else:
            return _image
    return PIECE_IMAGES[pieceName]
