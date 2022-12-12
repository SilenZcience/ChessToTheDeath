import pygame
from itertools import product
from os import path

import chess_to_the_death.util.engine as engine

BOARD_SIZE = (1024, 1024)
CELL_SIZE = (BOARD_SIZE[0] // engine.DIMENSION[0], BOARD_SIZE[1] // engine.DIMENSION[1])
IMAGE_OFFSET = 24
IMG_SIZE = tuple([size - (2*IMAGE_OFFSET) for size in CELL_SIZE])
MAX_FPS = 30
COLOR_WHITE = "#E6E6E6"
COLOR_BLACK = "#202124"
COLOR_HEALTH = "#FF0000"
COLORS = [tuple(int(COLOR_WHITE[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_BLACK[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_HEALTH[i:i+2], 16) for i in (1, 3, 5))]
PIECE_IMAGES = {}
workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)


def loadImages(gameState):
    basePath = path.join(workingDir, 'images')
    for piece in gameState.pieces:
        piece.image = pygame.transform.scale(
            pygame.image.load(path.join(basePath, piece._player + piece._name + '.png')),
            IMG_SIZE
        )


def drawBoard(mainScreen):
    for x in product(range(engine.DIMENSION[0]), range(engine.DIMENSION[1])):
        pygame.draw.rect(mainScreen, COLORS[sum(x) % 2],
                         pygame.Rect(x[0] * CELL_SIZE[0],
                                     x[1] * CELL_SIZE[1],
                                     *CELL_SIZE))


def drawPieces(mainScreen, gameState):
    for piece in gameState.pieces:
        mainScreen.blit(piece.image,
                        pygame.Rect(piece.cell_x * CELL_SIZE[0] + IMAGE_OFFSET,
                                    piece.cell_y * CELL_SIZE[1] + IMAGE_OFFSET,
                                    *IMG_SIZE))
        pygame.draw.rect(mainScreen, COLORS[2],
                         pygame.Rect(
                             piece.cell_x * CELL_SIZE[0] + (CELL_SIZE[0]//10),
                             (piece.cell_y + 1) * CELL_SIZE[1] - IMAGE_OFFSET + (CELL_SIZE[0]//10),
                             (piece.health * (CELL_SIZE[0] - (CELL_SIZE[0]//5)))//piece.maxHealth,
                             IMAGE_OFFSET // 3)
                         )


def mainGUI():
    pygame.init()
    pygame.display.set_caption('Chess to the Death')
    pygame.display.set_icon(pygame.image.load(
        path.join(workingDir, 'images/blackp.png')))
    mainScreen = pygame.display.set_mode(BOARD_SIZE)

    clock = pygame.time.Clock()
    gameState = engine.GameState()
    loadImages(gameState)
    
    selectedCells = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(selectedCells)
                col, row = pygame.mouse.get_pos()
                col = col // CELL_SIZE[0]
                row = row // CELL_SIZE[1]
                piece = gameState.getPiece(col, row)
                if not selectedCells:
                    if piece and gameState.selectablePiece(piece):
                        selectedCells.append(piece)
                else:
                    print(selectedCells)
                    if gameState.move(selectedCells[0], col, row):
                        selectedCells.clear()
                        gameState.nextTurn()
                    elif piece and gameState.selectablePiece(piece):
                        selectedCells[0] = gameState.getPiece(col, row)
            
        drawBoard(mainScreen)
        drawPieces(mainScreen, gameState)

        clock.tick(MAX_FPS)
        pygame.display.flip()
