import pygame
from itertools import product

import chess_to_the_death.util.engine as engine
import chess_to_the_death.util.fpsClock as fpsClock
from chess_to_the_death.util.loader import loadImage

BOARD_SIZE = (1024, 1024)
CELL_SIZE = (BOARD_SIZE[0] // engine.DIMENSION[0],
             BOARD_SIZE[1] // engine.DIMENSION[1])
HALF_CELL_SIZE = (CELL_SIZE[0]//2, CELL_SIZE[1]//2)
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


class Holder:
    selectedCell, winner = None, None
    options_move, options_attack = [], []
    attack_icon = None
    fps = None


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


def drawGame(mainScreen, gameState, holder):
    drawBoard(mainScreen)
    highlightCells(mainScreen, holder.selectedCell,  holder.options_move,  holder.options_attack)
    drawPieces(mainScreen, gameState,  holder.attack_icon)
    drawWinner(mainScreen,  holder.winner)


def renderGame(mainScreen, gameState, holder):
    drawGame(mainScreen, gameState, holder)
    holder.fps.render(mainScreen)
    pygame.display.flip()


def drawPromoteOptions(mainScreen, piece, promoteOptions):
    pygame.draw.rect(mainScreen, COLORS[(piece.cell_col+piece.cell_row) % 2],
                     pygame.Rect(piece.cell_col * CELL_SIZE[0],
                                 piece.cell_row * CELL_SIZE[1],
                                 *CELL_SIZE))
    for row in promoteOptions:
        for option in row:
            mainScreen.blit(
                option[0],
                pygame.Rect(*option[1]))


def renderPromoteOptions(mainScreen, gameState, holder):
    piece = holder.selectedCell
    currentPlayer = gameState.currentPlayer()
    promoteOptions = [['n', 'b'], ['r', 'q']]
    promoteOptionsDimensions = [[(loadImage(currentPlayer+'n', HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0],
                                   piece.cell_row * CELL_SIZE[1],
                                   *HALF_CELL_SIZE)),
                                 (loadImage(currentPlayer+'b', HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0] + HALF_CELL_SIZE[0],
                                     piece.cell_row * CELL_SIZE[1],
                                     *HALF_CELL_SIZE))],
                                [(loadImage(currentPlayer+'r', HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0],
                                    piece.cell_row *
                                   CELL_SIZE[1] + HALF_CELL_SIZE[1],
                                    *HALF_CELL_SIZE)),
                                 (loadImage(currentPlayer+'q', HALF_CELL_SIZE),
                                    (piece.cell_col * CELL_SIZE[0] + HALF_CELL_SIZE[0],
                                     piece.cell_row *
                                     CELL_SIZE[1] + HALF_CELL_SIZE[1],
                                     *HALF_CELL_SIZE))]]
    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                col, row = pygame.mouse.get_pos()
                col = (col*2) // CELL_SIZE[0]
                row = (row*2) // CELL_SIZE[1]
                if (col//2 == holder.selectedCell.cell_col) and (
                        row//2 == holder.selectedCell.cell_row):
                    col = col-(2*holder.selectedCell.cell_col)
                    row = row-(2*holder.selectedCell.cell_row)
                    gameState.promotePiece(
                        holder.selectedCell, promoteOptions[row][col])
                    selecting = False
        drawGame(mainScreen, gameState, holder)
        drawPromoteOptions(mainScreen, holder.selectedCell,
                           promoteOptionsDimensions)
        holder.fps.render(mainScreen)
        pygame.display.flip()
    return True


def newGame(holder):
    holder.selectedCell, holder.winner = None, None
    holder.options_move, holder.options_attack = [], []
    return engine.GameState(IMG_SIZE)


def mainGUI():
    holder = Holder()
    pygame.init()
    pygame.display.set_caption('Chess to the Death')
    pygame.display.set_icon(loadImage("blackp", (20, 20)))
    mainScreen = pygame.display.set_mode(BOARD_SIZE)

    holder.fps = fpsClock.FPS(MAX_FPS, BOARD_SIZE[0]-30, 0)
    gameState = newGame(holder)
    holder.attack_icon = loadImage("damage", (20, 20))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not holder.winner:
                col, row = pygame.mouse.get_pos()
                col = col // CELL_SIZE[0]
                row = row // CELL_SIZE[1]
                piece = gameState.getPiece(col, row)
                print("Selected:", piece, col, row)
                if not holder.selectedCell:
                    if piece and gameState.selectablePiece(piece):
                        holder.selectedCell = piece
                        holder.options_move, holder.options_attack = gameState.getOptions(piece)
                else:
                    if (gameState.move(holder.selectedCell, col, row, holder.options_move)) or (
                            gameState.attack(holder.selectedCell, col, row, holder.options_attack)):
                        if gameState.promotePawnOption(holder.selectedCell):
                            running = renderPromoteOptions(mainScreen, gameState, holder)
                            print("Pawn promoted!")
                        holder.selectedCell = None
                        holder.options_move, holder.options_attack = [], []
                        holder.winner = gameState.playerWon()
                        if not holder.winner:
                            gameState.createBoard()
                            renderGame(mainScreen, gameState, holder)
                            pygame.time.delay(250)
                            gameState.nextTurn()
                    elif piece and gameState.selectablePiece(piece):
                        if piece == holder.selectedCell:
                            piece = None
                        holder.selectedCell = piece
                        holder.options_move, holder.options_attack = gameState.getOptions(piece)
            if event.type == pygame.KEYDOWN and holder.winner:
                if pygame.key.name(event.key) == 'r':
                    print("Restarting...")
                    gameState = newGame(holder)

        renderGame(mainScreen, gameState, holder)
    print("GoodBye!")
