import pygame
from itertools import product
from time import sleep
from os import path

import chess_to_the_death.util.engine as engine
from chess_to_the_death.util.pieces import PIECES

BOARD_SIZE = (512, 512)
DIMENSION = (8, 8)
CELL_SIZE = (BOARD_SIZE[0] // DIMENSION[0], BOARD_SIZE[1] // DIMENSION[1])

MAX_FPS = 30
COLOR_WHITE = "#E6E6E6"
COLOR_BLACK = "#202124"
COLORS = [tuple(int(COLOR_WHITE[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_BLACK[i:i+2], 16) for i in (1, 3, 5))]
PIECE_IMAGES = {}
workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)


def loadImages():
    basePath = path.join(workingDir, 'images')
    for piece in PIECES:
        PIECE_IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(path.join(basePath, piece + '.png')),
            CELL_SIZE
        )


def drawBoard(mainScreen):
    for x in product(range(DIMENSION[0]), range(DIMENSION[1])):
        pygame.draw.rect(mainScreen, COLORS[sum(x) % 2],
                         pygame.Rect(x[0] * CELL_SIZE[0],
                                     x[1] * CELL_SIZE[1],
                                     *CELL_SIZE))


def drawPieces(mainScreen, gameState):
    for x in product(range(DIMENSION[0]), range(DIMENSION[1])):
        mainScreen.blit(PIECE_IMAGES['black_b'],
                        pygame.Rect(x[0] * CELL_SIZE[0],
                                    x[1] * CELL_SIZE[1],
                                    *CELL_SIZE))


def mainGUI():
    pygame.init()
    pygame.display.set_caption('Chess to the Death')
    pygame.display.set_icon(pygame.image.load(
        path.join(workingDir, 'images/black_p.png')))
    mainScreen = pygame.display.set_mode(BOARD_SIZE)

    clock = pygame.time.Clock()
    loadImages()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        drawBoard(mainScreen)
        drawPieces(mainScreen, None)

        clock.tick(MAX_FPS)
        pygame.display.flip()
