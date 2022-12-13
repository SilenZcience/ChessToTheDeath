import pygame
from itertools import product
from os import path

import chess_to_the_death.util.engine as engine
import chess_to_the_death.util.fpsClock as fpsClock

BOARD_SIZE = (1024, 1024)
CELL_SIZE = (BOARD_SIZE[0] // engine.DIMENSION[0],
             BOARD_SIZE[1] // engine.DIMENSION[1])
IMAGE_OFFSET = 24
IMG_SIZE = tuple([size - (2*IMAGE_OFFSET) for size in CELL_SIZE])
MAX_FPS = 30
COLORS = [(230, 230, 230), #"#E6E6E6" -> WHITE / CELL
          ( 32,  33,  36), #"#202124" -> DARK_GRAY / CELL
          (255,   0,   0), #"#FF0000" -> RED / HEALTH
          (  0,   0, 255), #"#0000FF" -> BLUE / SELECTED
          (  0, 255,   0), #"#00FF00" -> GREEN / MOVABLE
          (255,   0,   0), #"#FF0000" -> RED / ATTACKABLE
          ( 46, 149, 153), #"#2E9599" -> TEAL / TEXT
          (  0,   0,   0)] #"#000000" -> BLACK / REDO
PIECE_IMAGES = {}
workingDir = path.abspath(
    path.join(path.dirname(path.realpath(__file__)), '..')
)


def loadImage(relPath, size):
    basePath = path.join(workingDir, 'images')
    return pygame.transform.scale(
        pygame.image.load(path.join(basePath, relPath)),
        size
    )


def loadImages(gameState):
    imgDict = {}
    for piece in gameState.pieces:
        pieceName = piece._player + piece._name
        if pieceName in imgDict:
            piece.image = imgDict[pieceName]
            continue
        piece.image = imgDict[pieceName] = loadImage(pieceName + '.png', IMG_SIZE)


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
        highlightCell(mainScreen, piece.cell_col, piece.cell_row, COLORS[3])
    for option in options_move:
        highlightCell(mainScreen, option[0], option[1], COLORS[4])
    for option in options_attack:
        highlightCell(mainScreen, option[0], option[1], COLORS[5])


def drawPieces(mainScreen, gameState, attack_icon):
    for piece in gameState.pieces:
        mainScreen.blit(piece.image,
                        pygame.Rect(piece.cell_col * CELL_SIZE[0] + IMAGE_OFFSET,
                                    piece.cell_row * CELL_SIZE[1] + IMAGE_OFFSET,
                                    *IMG_SIZE))
        mainScreen.blit(attack_icon, (piece.cell_col * CELL_SIZE[0], piece.cell_row * CELL_SIZE[1]))
        font = pygame.font.SysFont("Verdana", 16)
        mainScreen.blit(font.render(str(piece.damage), True, COLORS[6]), 
                        (piece.cell_col * CELL_SIZE[0] + 25,
                         piece.cell_row * CELL_SIZE[1]))
        pygame.draw.rect(mainScreen, COLORS[2],
                         pygame.Rect(
                             piece.cell_col * CELL_SIZE[0] + (CELL_SIZE[0]//10),
                             (piece.cell_row + 1) * CELL_SIZE[1] - IMAGE_OFFSET + (CELL_SIZE[0]//10),
                             (piece.health * (CELL_SIZE[0] - (CELL_SIZE[0]//5)))//piece.maxHealth,
                             IMAGE_OFFSET // 3))
        font = pygame.font.SysFont("Verdana", 8)
        mainScreen.blit(font.render(str(piece.health) + "/" + str(piece.maxHealth), True, COLORS[6]), 
                        (piece.cell_col * CELL_SIZE[0] + (CELL_SIZE[0]//10),
                         (piece.cell_row + 1) * CELL_SIZE[1] - IMAGE_OFFSET))


def drawWinner(mainScreen, winner):
    if not winner:
        return
    font = pygame.font.SysFont("Verdana", 64)
    text = font.render(winner.upper() + " WON!", True, COLORS[6])
    text_size = (text.get_width(), text.get_height())
    text_location = pygame.Rect(0, 0, *BOARD_SIZE).move(BOARD_SIZE[0] / 2 - text_size[0] / 2,
                                                        BOARD_SIZE[1] / 2 - text_size[1] / 2)
    mainScreen.blit(text, text_location)
    font = pygame.font.SysFont("Verdana", 32)
    text = font.render("Play Again (R)", True, COLORS[7])
    text_location = pygame.Rect(0, 0, *BOARD_SIZE).move(BOARD_SIZE[0] / 2 - text.get_width() / 2,
                                                        BOARD_SIZE[1] / 2 + text_size[1] / 2)
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
    attack_icon = loadImage("damage.png", (20, 20))
    
    selectedCell, winner = None, None
    options_move, options_attack = [], []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not winner:
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
                        if piece == selectedCell:
                            piece = None
                        selectedCell = piece
                        options_move, options_attack = gameState.getOptions(
                            piece)
            if event.type == pygame.KEYDOWN and winner:
                if pygame.key.name(event.key) == 'r':
                    print("Restarting...")
                    gameState = engine.GameState()
                    loadImages(gameState)
                    selectedCell, winner = None, None
                    options_move, options_attack = [], []

        drawBoard(mainScreen)
        highlightCells(mainScreen, selectedCell, options_move, options_attack)
        drawPieces(mainScreen, gameState, attack_icon)
        drawWinner(mainScreen, winner)

        clock.render(mainScreen)
        pygame.display.flip()
