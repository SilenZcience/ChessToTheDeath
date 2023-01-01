from os import path
from pygame import image, transform

workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)
basePath = path.join(workingDir, 'images')
PIECE_IMAGES = {}


def loadImage(relPath: str, size: tuple):
    """
    Takes an image-name (e.g. 'blackp') and a tuple
    containing the width, height.
    Returns a pygame.Surface image.
    """
    if not size:
        return None
    if not (relPath + str(size[0]) + "x" + str(size[1])) in PIECE_IMAGES:
        PIECE_IMAGES[relPath + str(size[0]) + "x" + str(size[1])] = transform.smoothscale(
            image.load(path.join(basePath, relPath + ".png")), size)
    return PIECE_IMAGES[relPath + str(size[0]) + "x" + str(size[1])]
