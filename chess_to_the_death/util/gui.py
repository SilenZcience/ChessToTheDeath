from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide' # sorry, pygame

import pygame
from itertools import product

import chess_to_the_death.util.engine as engine
import chess_to_the_death.util.fpsClock as fpsClock
import chess_to_the_death.parser.argparser as argparser
from chess_to_the_death.util.loader import loadImage, clearPieceImageCache
from chess_to_the_death.entity.pieces import Piece # only for type-hints


BOARD_SIZE = (1044, 1044)
BOARD_OFFSET = (BOARD_SIZE[0] // 50, # 2% for cell identifiers
                BOARD_SIZE[1] // 50)
CELL_SIZE = ((BOARD_SIZE[0] - BOARD_OFFSET[0])// engine.DIMENSION[1],
             (BOARD_SIZE[1] - BOARD_OFFSET[1]) // engine.DIMENSION[0])
HALF_CELL_SIZE = (CELL_SIZE[0]//2, CELL_SIZE[1]//2)
IDENTIFIER_OFFSET = (engine.DIMENSION[1] * CELL_SIZE[0],
                     engine.DIMENSION[0] * CELL_SIZE[1])
IMG_SIZE = (int(CELL_SIZE[0] * 0.75), # image is 3/4 the size of the cell
            int(CELL_SIZE[1] * 0.75))
IMAGE_OFFSET = (int(CELL_SIZE[0] * 0.125), # half of the remaining 1/4 -> 1/8
                int(CELL_SIZE[1] * 0.125))

COLORS = [(230, 230, 230, 255), #"#E6E6E6" -> WHITE / CELL + HOVER
          ( 32,  33,  36, 255), #"#202124" -> DARK_GRAY / CELL + HOVER
          (255,   0,   0, 255), #"#FF0000" -> RED / HEALTH
          (  0,   0, 255, 255), #"#0000FF" -> BLUE / SELECTED
          (  0, 255,   0, 255), #"#00FF00" -> GREEN / MOVABLE
          (255,   0,   0, 255), #"#FF0000" -> RED / ATTACKABLE
          ( 46, 149, 153, 255), #"#2E9599" -> TEAL / TEXT
          (  0,   0,   0, 255), #"#000000" -> BLACK / REDO
          (255, 165,   0, 150)] # '#FFA500' -> ORANGE / PLANNING_ARROWS


class Holder:
    selectedCell: Piece = None
    winner: str = ''
    options_move, options_attack = [], []
    marked_cells = []
    planning_arrows = []
    attack_icon: pygame.Surface = None
    fps: fpsClock = None


def getMouseCell(halfCell: bool = False) -> tuple:
    """
    gets the current cell (column, row) at
    the mouse position.
    measures in half cells if 'halfCell' is True, this
    is needed for the promotionOptions.
    """
    col, row = pygame.mouse.get_pos()
    if halfCell:
        col *= 2
        row *= 2
    return (col // CELL_SIZE[0], row // CELL_SIZE[1])


def drawBoard(mainScreen: pygame.Surface) -> None:
    """
    Draws the black and white background cells.
    """
    for x in product(range(engine.DIMENSION[1]), range(engine.DIMENSION[0])):
        pygame.draw.rect(mainScreen, COLORS[sum(x) % 2],
                         pygame.Rect(x[0] * CELL_SIZE[0],
                                     x[1] * CELL_SIZE[1],
                                     *CELL_SIZE))


def highlightCell(mainScreen: pygame.Surface, x: int, y: int, w: int, h: int, color: tuple, alpha: int = 75) -> None:
    """
    Highlights a single cell at the coordinates x,y
    with the width 'w' and height 'h' and
    with the 'color' given as a tuple (R, G, B).
    """
    highlight = pygame.Surface((w, h))
    highlight.set_alpha(alpha)
    highlight.fill(color)
    return mainScreen.blit(highlight, (x, y))


def highlightCells(mainScreen: pygame.Surface, piece: Piece, options_move: list, options_attack: list, marked_cells: set) -> None:
    """
    Highlights the selected cell.
    Highlights the valid moves of the selected cell.
    Highlights the valid attacks of the selected cell.
    """
    if piece:
        highlightCell(mainScreen, piece.cell_col * CELL_SIZE[0],
                      piece.cell_row * CELL_SIZE[1],
                      *CELL_SIZE, COLORS[3])
        for option in options_move:
            highlightCell(mainScreen, option[0] * CELL_SIZE[0],
                        option[1] * CELL_SIZE[1],
                        *CELL_SIZE, COLORS[4])
        for option in options_attack:
            highlightCell(mainScreen, option[0] * CELL_SIZE[0],
                        option[1] * CELL_SIZE[1],
                        *CELL_SIZE, COLORS[5])
    for cell in marked_cells:
        highlightCell(mainScreen, cell[0] * CELL_SIZE[0],
                        cell[1] * CELL_SIZE[1],
                        *CELL_SIZE, COLORS[2], 150)
    
    if not argparser.HIGHLIGHT_CELLS:
        return
    col, row = getMouseCell()
    if 0 <= col < engine.DIMENSION[1] and 0 <= row < engine.DIMENSION[0]:
        highlightCell(mainScreen, col * CELL_SIZE[0], row * CELL_SIZE[1], *CELL_SIZE, COLORS[1 - ((col+row) % 2)])


def drawPieces(mainScreen: pygame.Surface, gameState: engine.GameState, attack_icon: pygame.Surface) -> None:
    """
    Draws all pieces of the engine.board, including their health- and attackvalues
    """
    for piece in gameState.pieces:
        mainScreen.blit(piece.image,
                        pygame.Rect(piece.cell_col * CELL_SIZE[0] + IMAGE_OFFSET[0],
                                    piece.cell_row * CELL_SIZE[1] + IMAGE_OFFSET[1],
                                    *IMG_SIZE))
        if argparser.DEFAULT_MODE:
            continue
        mainScreen.blit(attack_icon, (piece.cell_col * CELL_SIZE[0], piece.cell_row * CELL_SIZE[1]))
        font = pygame.font.SysFont("Verdana", int(16 * ((min(CELL_SIZE)/128))))
        mainScreen.blit(font.render(str(piece.damage), True, COLORS[6]),
                        (piece.cell_col * CELL_SIZE[0] + BOARD_OFFSET[0],
                         piece.cell_row * CELL_SIZE[1]))
        pygame.draw.rect(mainScreen, COLORS[2],
                         pygame.Rect(
                             piece.cell_col * CELL_SIZE[0] + (IMAGE_OFFSET[0]//2),
                             (piece.cell_row + 1) * CELL_SIZE[1] - (IMAGE_OFFSET[1]//2),
                             (piece.health * (CELL_SIZE[0] - IMAGE_OFFSET[0]))//piece.maxHealth,
                             IMAGE_OFFSET[1] // 3))
        font = pygame.font.SysFont("Verdana", int(10 * ((min(CELL_SIZE)/128))))
        text = font.render(str(piece.health), True, COLORS[6])
        text_size = (text.get_width(), text.get_height())
        text_location = pygame.Rect(piece.cell_col * CELL_SIZE[0] + (IMAGE_OFFSET[0]//2),
                                    (piece.cell_row + 1) * CELL_SIZE[1] - IMAGE_OFFSET[1] - text_size[1] // 2,
                                    IMAGE_OFFSET[0]//2,
                                    IMAGE_OFFSET[1]//2)
        mainScreen.blit(text, text_location)
        text = font.render(str(piece.maxHealth), True, COLORS[6])
        text_size = (text.get_width(), text.get_height())
        text_location = pygame.Rect((piece.cell_col + 1) * CELL_SIZE[0] - IMAGE_OFFSET[0] - text_size[0] // 2,
                                    (piece.cell_row + 1) * CELL_SIZE[1] - IMAGE_OFFSET[1] - text_size[1] // 2,
                                    IMAGE_OFFSET[0]//2,
                                    IMAGE_OFFSET[1]//2)
        mainScreen.blit(text, text_location)


def drawWinner(mainScreen: pygame.Surface, winner: str) -> None:
    """
    If a player has won this function will display the win-message
    on the 'mainScreen'.
    """
    if not winner:
        return
    font = pygame.font.SysFont("Verdana", int(64 * ((min(CELL_SIZE)/128))))
    text = font.render(winner.upper(), True, COLORS[6])
    text_size = (text.get_width(), text.get_height())
    text_location = pygame.Rect(BOARD_SIZE[0] // 2 - text_size[0] // 2,
                                BOARD_SIZE[1] // 2 - text_size[1] // 2, *text_size)
    mainScreen.blit(text, text_location)
    font = pygame.font.SysFont("Verdana", int(32 * ((min(CELL_SIZE)/128))))
    text = font.render("Play Again (R)", True, COLORS[7])
    text_location = pygame.Rect(BOARD_SIZE[0] // 2 - text.get_width() // 2,
                                BOARD_SIZE[1] // 2 + text_size[1] // 2,
                                text.get_width(), text.get_height())
    mainScreen.blit(text, text_location)


def draw_polygon_alpha(mainScreen, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    return mainScreen.blit(shape_surf, target_rect)


def drawArrow(mainScreen: pygame.Surface, start: pygame.Vector2, end: pygame.Vector2,
        color: tuple, body_width: int = 2, head_width: int = 4, head_height: int = 2):
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    headPoly = draw_polygon_alpha(mainScreen, color, head_verts)
    bodyPoly = None
    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start
        bodyPoly = draw_polygon_alpha(mainScreen, color, body_verts)
    return [headPoly, bodyPoly]


def drawIdentifiers(mainScreen: pygame.Surface, gameState: engine.GameState):
    """
    Draw the letters and numbers to identify a single cell.
    Only needs to happen once a move.
    """
    # Draw the Background for the Cell Identifiers
    right_background = pygame.draw.rect(mainScreen, COLORS[1],
                         pygame.Rect(IDENTIFIER_OFFSET[0], 0,
                                     BOARD_SIZE[0] - IDENTIFIER_OFFSET[0], BOARD_SIZE[1]))
    bottom_background = pygame.draw.rect(mainScreen, COLORS[1],
                         pygame.Rect(0, IDENTIFIER_OFFSET[1],
                                     BOARD_SIZE[0], BOARD_SIZE[1] - IDENTIFIER_OFFSET[1]))
    pygame.display.update(right_background)
    pygame.display.update(bottom_background)
    
    # Scale the Font according to the CELL_SIZE
    font = pygame.font.SysFont("Verdana", int(16 * ((min(CELL_SIZE)/128))))
    
    # Draw the Number-Identifiers at the right side
    for i in range(engine.DIMENSION[0]):
        text = font.render(gameState.numbers_identifiers[i], True, COLORS[6])
        text_size = (text.get_width(), text.get_height())
        text_location = pygame.Rect(IDENTIFIER_OFFSET[0] + (BOARD_OFFSET[0] - text_size[0]) // 2,
                                    (i * CELL_SIZE[1]) + HALF_CELL_SIZE[1] - (text_size[1] // 2),
                                    BOARD_OFFSET[0], CELL_SIZE[1])
        identifier = mainScreen.blit(text, text_location)
        pygame.display.update(identifier)
        
    # Draw the Letter-Identifiers at the bottom
    for i in range(engine.DIMENSION[1]):
        text = font.render(gameState.alpha_identifiers[i], True, COLORS[6])
        text_size = (text.get_width(), text.get_height())
        text_location = pygame.Rect((i * CELL_SIZE[0]) + HALF_CELL_SIZE[0] - (text_size[0] // 2),
                                    IDENTIFIER_OFFSET[1] + (BOARD_OFFSET[1] - text_size[1]) // 2,
                                    CELL_SIZE[0], BOARD_OFFSET[1])
        identifier = mainScreen.blit(text, text_location)
        pygame.display.update(identifier)


def drawGame(mainScreen: pygame.Surface, gameState: engine.GameState, holder: Holder) -> None:
    drawBoard(mainScreen)
    highlightCells(mainScreen, holder.selectedCell, holder.options_move, holder.options_attack, holder.marked_cells)
    drawPieces(mainScreen, gameState, holder.attack_icon)
    drawWinner(mainScreen, holder.winner)


def renderGame(mainScreen: pygame.Surface, gameState: engine.GameState, holder: Holder) -> None:
    """
    Draws the Game, the Fps-display and updates the screen.
    """
    drawGame(mainScreen, gameState, holder)
    if argparser.HIGHLIGHT_CELLS:
        holder.fps.render(mainScreen)
    arrow_thickness = 2 * min(IMAGE_OFFSET)
    for arrow in holder.planning_arrows:
        drawArrow(mainScreen, arrow[0], arrow[1], COLORS[8], arrow_thickness, 2 * arrow_thickness, arrow_thickness)
    pygame.display.flip()


def drawPromoteOptions(mainScreen: pygame.Surface, piece: Piece, promoteOptions: list) -> None:
    """
    If a pawn can be promoted this function will draw the four promoteOptions on the
    cell at which the pawn stands, aswell as the hover-highlight effect for
    said options.
    """
    pygame.draw.rect(mainScreen, COLORS[(piece.cell_col+piece.cell_row) % 2],
                     pygame.Rect(piece.cell_col * CELL_SIZE[0],
                                 piece.cell_row * CELL_SIZE[1],
                                 *CELL_SIZE))
    
    col, row = getMouseCell(True)
    if (col//2 == piece.cell_col) and (row//2 == piece.cell_row):
        highlightedArea = highlightCell(mainScreen, (col//2) * CELL_SIZE[0] + (HALF_CELL_SIZE[0] * (col % 2)),
                    (row//2) * CELL_SIZE[1] + (HALF_CELL_SIZE[1] * (row % 2)),
                    *HALF_CELL_SIZE, COLORS[3])
        pygame.display.update(highlightedArea)
    for options in promoteOptions:
        for option in options:
            promoteOption = mainScreen.blit(option[0], pygame.Rect(*option[1]))
            pygame.display.update(promoteOption)


def choosePromoteOptions(mainScreen: pygame.Surface, gameState: engine.GameState, holder: Holder) -> bool:
    """
    Takes over the main Loop, until the player has decided to which piece he/she wants to
    promote the pawn (holder.selectedCell).
    
    Returns a boolean in case the game is being quit.
    """
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
    
    drawGame(mainScreen, gameState, holder)
    pygame.display.flip()
    while True:
        pygame.time.delay(25) # relieve the CPU a bit ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                col, row = getMouseCell(True)
                if (col//2 == holder.selectedCell.cell_col) and (
                        row//2 == holder.selectedCell.cell_row):
                    col = col-(2*holder.selectedCell.cell_col)
                    row = row-(2*holder.selectedCell.cell_row)
                    gameState.promotePiece(holder.selectedCell, promoteOptions[row][col])
                    return True
        drawPromoteOptions(mainScreen, holder.selectedCell, promoteOptionsDimensions)


def rescaleWindow(newWidth: int, newHeight: int, holder: Holder, gameState: engine.GameState):
    global BOARD_SIZE
    global BOARD_OFFSET
    global CELL_SIZE
    global HALF_CELL_SIZE
    global IDENTIFIER_OFFSET
    global IMG_SIZE
    global IMAGE_OFFSET
    
    CELL_SIZE_OLD = CELL_SIZE
    BOARD_SIZE = (newWidth, newHeight)
    BOARD_OFFSET = (BOARD_SIZE[0] // 50, 
                    BOARD_SIZE[1] // 50)
    CELL_SIZE = ((BOARD_SIZE[0] - BOARD_OFFSET[0])// engine.DIMENSION[1],
                (BOARD_SIZE[1] - BOARD_OFFSET[1]) // engine.DIMENSION[0])
    HALF_CELL_SIZE = (CELL_SIZE[0]//2, CELL_SIZE[1]//2)
    IDENTIFIER_OFFSET = (engine.DIMENSION[1] * CELL_SIZE[0],
                        engine.DIMENSION[0] * CELL_SIZE[1])
    IMG_SIZE = (int(CELL_SIZE[0] * 0.75),
                int(CELL_SIZE[1] * 0.75))
    IMAGE_OFFSET = (int(CELL_SIZE[0] * 0.125),
                    int(CELL_SIZE[1] * 0.125))


    holder.fps = fpsClock.FPS(argparser.MAX_FPS, BOARD_SIZE[0]-30-BOARD_OFFSET[0], 0)
    holder.attack_icon = loadImage("damage", BOARD_OFFSET)
    
    clearPieceImageCache()
    for piece in gameState.pieces:
        piece.loadImage(IMG_SIZE)
        
    for arrow in holder.planning_arrows:
        arrow[0][0] = (arrow[0][0] - (CELL_SIZE_OLD[0] // 2)) // CELL_SIZE_OLD[0]
        arrow[0][1] = (arrow[0][1] - (CELL_SIZE_OLD[1] // 2)) // CELL_SIZE_OLD[1]
        arrow[1][0] = (arrow[1][0] - (CELL_SIZE_OLD[0] // 2)) // CELL_SIZE_OLD[0]
        arrow[1][1] = (arrow[1][1] - (CELL_SIZE_OLD[1] // 2)) // CELL_SIZE_OLD[1]
        
        arrow[0][0] = arrow[0][0] * CELL_SIZE[0] + (CELL_SIZE[0] // 2)
        arrow[0][1] = arrow[0][1] * CELL_SIZE[1] + (CELL_SIZE[1] // 2)
        arrow[1][0] = arrow[1][0] * CELL_SIZE[0] + (CELL_SIZE[0] // 2)
        arrow[1][1] = arrow[1][1] * CELL_SIZE[1] + (CELL_SIZE[1] // 2)
    
    
def newGame(holder: Holder) -> engine.GameState:
    """
    Resets all values and starts/returns a new engine.GameState.
    """
    holder.selectedCell, holder.winner = None, None
    holder.options_move, holder.options_attack = [], []
    return engine.GameState(IMG_SIZE)


def mainGUI():
    holder = Holder()
    pygame.init()
    mainScreen = pygame.display.set_mode(BOARD_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption('Chess to the Death')
    pygame.display.set_icon(loadImage("blackp", (20, 20)))
    pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                              pygame.KEYDOWN, pygame.VIDEORESIZE])
    
    holder.fps = fpsClock.FPS(argparser.MAX_FPS, BOARD_SIZE[0]-30-BOARD_OFFSET[0], 0)
    gameState = newGame(holder)
    holder.attack_icon = loadImage("damage", BOARD_OFFSET)
    sel_col, sel_row = -1, -1
    
    drawIdentifiers(mainScreen, gameState)
    renderGame(mainScreen, gameState, holder)
    
    running = True
    while running:
        if argparser.HIGHLIGHT_CELLS:
            renderGame(mainScreen, gameState, holder)
        pygame.time.delay(25) # relieve the CPU a bit ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Log:")
                print(gameState.action_log)
            elif event.type == pygame.MOUSEBUTTONDOWN and not holder.winner:
                col, row = getMouseCell()
                if event.button == 1:
                    holder.marked_cells.clear()
                    holder.planning_arrows.clear()
                    piece = gameState.getPiece(col, row)
                    print("Selected:", piece, col, row)
                    if not holder.selectedCell:
                        if piece and gameState.selectablePiece(piece):
                            holder.selectedCell = piece
                            holder.options_move, holder.options_attack = gameState.getOptions(piece)
                    else:
                        if gameState.action(holder.selectedCell, col, row, holder.options_move, holder.options_attack):
                            holder.options_move, holder.options_attack = [], []
                            if gameState.promotePawnOption(holder.selectedCell):
                                print("Choose Pawn Promotion...")
                                running = choosePromoteOptions(mainScreen, gameState, holder)
                                print("Pawn promoted!")
                            if running:
                                holder.selectedCell = None
                                holder.winner = gameState.playerWon()
                                renderGame(mainScreen, gameState, holder)
                                if not holder.winner:
                                    pygame.time.delay(250)
                                    gameState.nextTurn()
                                    drawIdentifiers(mainScreen, gameState)
                        elif piece and gameState.selectablePiece(piece):
                            if piece == holder.selectedCell:
                                piece = None
                            holder.selectedCell = piece
                            holder.options_move, holder.options_attack = gameState.getOptions(piece)
                    renderGame(mainScreen, gameState, holder)
                elif event.button == 3:
                    sel_col, sel_row = col, row
            elif event.type == pygame.MOUSEBUTTONUP and not holder.winner:
                col, row = getMouseCell()
                if event.button == 3:
                    sel_col = min(sel_col, engine.DIMENSION[1]-1)
                    sel_row = min(sel_row, engine.DIMENSION[0]-1)
                    col = min(col, engine.DIMENSION[1]-1)
                    row = min(row, engine.DIMENSION[0]-1)
                    
                    planningBlit = None
                    if sel_col == col and sel_row == row:
                        nextMark = (col, row)
                        if not nextMark in holder.marked_cells:
                            holder.marked_cells.append(nextMark)
                            planningBlit = highlightCell(mainScreen, col * CELL_SIZE[0],
                                        row * CELL_SIZE[1],
                                        *CELL_SIZE, COLORS[2], 150)
                    else:
                        newArrow = (pygame.Vector2(sel_col * CELL_SIZE[0] + CELL_SIZE[0]//2,
                                                   sel_row * CELL_SIZE[1] + CELL_SIZE[1]//2),
                                    pygame.Vector2(col * CELL_SIZE[0] + CELL_SIZE[0]//2,
                                                   row * CELL_SIZE[1] + CELL_SIZE[1]//2))
                        # if not newArrow in holder.planning_arrows:
                        holder.planning_arrows.append(newArrow)
                        arrow_thickness = 2 * min(IMAGE_OFFSET)
                        planningBlit = drawArrow(mainScreen, newArrow[0], newArrow[1], COLORS[8],
                                                    arrow_thickness, 2 * arrow_thickness, arrow_thickness)
                    pygame.display.update(planningBlit)
            elif event.type == pygame.KEYDOWN and holder.winner:
                if pygame.key.name(event.key) == 'r':
                    print("Log:")
                    print(gameState.action_log)
                    print("Restarting...")
                    gameState = newGame(holder)
                    renderGame(mainScreen, gameState, holder)
            elif event.type == pygame.VIDEORESIZE:
                rescaleWindow(event.w, event.h, holder, gameState)
                mainScreen = pygame.display.set_mode(BOARD_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE)
                drawIdentifiers(mainScreen, gameState)
                renderGame(mainScreen, gameState, holder)
    pygame.quit()
    print("GoodBye!")
