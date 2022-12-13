import pygame
from itertools import product
from os import path

import chess_to_the_death.util.engine as engine
import chess_to_the_death.util.fpsClock as fpsClock

BOARD_SIZE = (1024, 1024)
CELL_SIZE = (BOARD_SIZE[0] // engine.DIMENSION[0], BOARD_SIZE[1] // engine.DIMENSION[1])
IMAGE_OFFSET = 24
IMG_SIZE = tuple([size - (2*IMAGE_OFFSET) for size in CELL_SIZE])
MAX_FPS = 30
COLOR_WHITE = "#E6E6E6"
COLOR_BLACK = "#202124"
COLOR_HEALTH = "#FF0000"
COLOR_SELECTED = "#0000FF"
COLOR_MOVABLE = "#00FF00"
COLOR_ATTACKABLE = "#FF0000"
COLOR_WINNER = "#2E9599"
COLORS = [tuple(int(COLOR_WHITE[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_BLACK[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_HEALTH[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_SELECTED[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_MOVABLE[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_ATTACKABLE[i:i+2], 16) for i in (1, 3, 5)),
          tuple(int(COLOR_WINNER[i:i+2], 16) for i in (1, 3, 5))]
PIECE_IMAGES = {}
workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)


def loadImages(gameState):
    basePath = path.join(workingDir, 'images')
    imgDict = {}
    for piece in gameState.pieces:
        pieceName = piece._player + piece._name
        if pieceName in imgDict:
            piece.image = imgDict[pieceName]
            continue
        piece.image = imgDict[pieceName] = pygame.transform.scale(
            pygame.image.load(path.join(basePath, pieceName + '.png')),
            IMG_SIZE
        )


def drawBoard(mainScreen):
    for x in product(range(engine.DIMENSION[0]), range(engine.DIMENSION[1])):
        pygame.draw.rect(mainScreen, COLORS[sum(x) % 2],
                         pygame.Rect(x[0] * CELL_SIZE[0],
                                     x[1] * CELL_SIZE[1],
                                     *CELL_SIZE))


def highlightCell(mainScreen, x, y, color):
    highlight = pygame.Surface(CELL_SIZE)
    highlight.set_alpha(75)
    highlight.fill(color)
    mainScreen.blit(highlight, (x * CELL_SIZE[0], y * CELL_SIZE[1]))


def highlightCells(mainScreen, piece, options_move, options_attack):
    if piece:
        highlightCell(mainScreen, piece.cell_x, piece.cell_y, COLORS[3])
    for option in options_move:
        highlightCell(mainScreen, option[1], option[0], COLORS[4])
    for option in options_attack:
        highlightCell(mainScreen, option[1], option[0], COLORS[5])


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


def drawWinner(mainScreen, winner):
    if not winner:
        return
    font = pygame.font.SysFont("Verdana", 64)
    text = font.render(winner.upper() + " WON!", True, COLORS[6])
    text_location = pygame.Rect(0, 0, *BOARD_SIZE).move(BOARD_SIZE[0] / 2 - text.get_width() / 2,
                                                        BOARD_SIZE[1] / 2 - text.get_height() / 2)
    mainScreen.blit(text, text_location)   


def mainGUI():
    pygame.init()
    pygame.display.set_caption('Chess to the Death')
    pygame.display.set_icon(pygame.image.load(
        path.join(workingDir, 'images/blackp.png')))
    mainScreen = pygame.display.set_mode(BOARD_SIZE)

    clock = fpsClock.FPS(MAX_FPS, BOARD_SIZE[0]-30, 0)
    gameState = engine.GameState()
    loadImages(gameState)
    
    selectedCell, winner = None, None
    options_move, options_attack = [], []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not winner:
                    col, row = pygame.mouse.get_pos()
                    col = col // CELL_SIZE[0]
                    row = row // CELL_SIZE[1]
                    piece = gameState.getPiece(col, row)
                    print("Selected:", piece, col, row)
                    if not selectedCell:
                        if piece and gameState.selectablePiece(piece):
                            selectedCell = piece
                            options_move, options_attack = gameState.getOptions(piece)
                    else:
                        if (gameState.move(selectedCell, col, row, options_move)) or (
                            gameState.attack(selectedCell, col, row, options_attack)):
                            selectedCell = None
                            options_move, options_attack = [], []
                            winner = gameState.playerWon()
                            if not winner:
                                gameState.nextTurn()
                        elif piece and gameState.selectablePiece(piece):
                            selectedCell = piece
                            options_move, options_attack = gameState.getOptions(piece)
            
        drawBoard(mainScreen)
        highlightCells(mainScreen, selectedCell, options_move, options_attack)
        drawPieces(mainScreen, gameState)
        drawWinner(mainScreen, winner)
        
        clock.render(mainScreen)
        pygame.display.flip()
