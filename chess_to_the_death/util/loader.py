from os import path, pardir
from pygame import image, transform, Surface

workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), pardir)
)

basePath = path.join(workingDir, 'media', 'images')
PIECE_IMAGES = {}


def loadImage(relPath: str, size: tuple) -> Surface:
    """
    Takes an image-name (e.g. 'blackp') and a tuple
    containing the width, height.
    Returns a pygame.Surface image.
    """
    if not size:
        return None
    if (relPath + str(size[0]) + 'x' + str(size[1])) not in PIECE_IMAGES:
        PIECE_IMAGES[relPath + str(size[0]) + 'x' + str(size[1])] = transform.smoothscale(
            image.load(path.join(basePath, relPath + '.png')).convert_alpha(), size)
    return PIECE_IMAGES[relPath + str(size[0]) + "x" + str(size[1])]

def clearPieceImageCache() -> None:
    """
    clear image cache
    """
    global PIECE_IMAGES
    PIECE_IMAGES = {}