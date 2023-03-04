from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'  # sorry, pygame

import pygame
from itertools import product

import chess_to_the_death.parser.argparser as argparser
import chess_to_the_death.util.fpsClock as fpsClock
import chess_to_the_death.util.engine as engine
from chess_to_the_death.entity.pieces import Piece  # only for type-hints
from chess_to_the_death.util.loader import loadImage, clearPieceImageCache
from chess_to_the_death.util.definition import Outcome, PieceChar


BOARD_SIZE = (1044, 1044)
BOARD_OFFSET = (BOARD_SIZE[0] // 50,  # 2% for cell identifiers
                BOARD_SIZE[1] // 50)
CELL_SIZE = ((BOARD_SIZE[0] - BOARD_OFFSET[0]) // engine.DIMENSION[1],
             (BOARD_SIZE[1] - BOARD_OFFSET[1]) // engine.DIMENSION[0])
HALF_CELL_SIZE = (CELL_SIZE[0]//2, CELL_SIZE[1]//2)
IDENTIFIER_OFFSET = (engine.DIMENSION[1] * CELL_SIZE[0],
                     engine.DIMENSION[0] * CELL_SIZE[1])
IMG_SIZE = (int(CELL_SIZE[0] * 0.75),  # image is 3/4 the size of the cell
            int(CELL_SIZE[1] * 0.75))
IMAGE_OFFSET = (int(CELL_SIZE[0] * 0.125),  # half of the remaining 1/4 -> 1/8
                int(CELL_SIZE[1] * 0.125))

PLACEPIECE_QUIT, PLACEPIECE_PLACED, PLACEPIECE_ABORTED = range(3)

COLORS = [(230, 230, 230), #"#E6E6E6" -> WHITE / CELL + HOVER
          ( 45,  46,  48), #"#202124" -> DARK_GRAY / CELL + HOVER
          (255,   0,   0), #"#FF0000" -> RED / HEALTH
          (  0,   0, 255), #"#0000FF" -> BLUE / SELECTED
          (  0, 255,   0), #"#00FF00" -> GREEN / MOVABLE
          (255,   0,   0), #"#FF0000" -> RED / ATTACKABLE
          ( 46, 149, 153), #"#2E9599" -> TEAL / TEXT
          (  0,   0,   0), #"#000000" -> BLACK / REDO
          (255, 165,   0), #"#FFA500" -> ORANGE / PLANNING_ARROWS
          (218, 112, 214), #"#DA70D6" -> PINK / LAST MOVE
          ( 66, 245, 227)] #"#42F5E3" -> DARK TEAL / PLACE PIECE

# define a holder object to hold variables bundled in a global spectrum
# and instantiate it
class Holder:
    # Engine
    selectedPiece: Piece = None
    winner: str = ''
    options_move, options_attack = [], []
    last_move = []
    # Planning
    marked_cells_circle = set()
    marked_cells_square = set()
    planning_arrows = []
    # GUI
    attack_icon: pygame.Surface = None
    fps: fpsClock = None
    # Args
    # for performance reasons and avoidance of visual glitches we disable
    # cell hover highlighting during planning (arrows, marks)
    # we copy the original HIGHLIGHT_CELLS parameter, so we can backup
    # the given value later.
    highlight_cells = None


holder = Holder()

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


def draw_polygon_alpha(mainScreen: pygame.Surface, color: tuple, points: list, alpha: int = 150) -> None:
    """
    Draw a polygon from 'points' on the 'mainScreen'.
    Renders with alpha values.
    """
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    shape_surf.set_alpha(alpha)
    pygame.draw.polygon(shape_surf, color, [
                        (x - min_x, y - min_y) for x, y in points])
    mainScreen.blit(shape_surf, target_rect)
    pygame.display.update(target_rect)


def drawArrow(mainScreen: pygame.Surface, start: pygame.Vector2, end: pygame.Vector2,
              color: tuple, body_width: int = 2, head_width: int = 4, head_height: int = 2) -> None:
    """
    Draw a alpha-colored array on the 'mainScreen'
    """
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
    translation = pygame.Vector2(
        0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    draw_polygon_alpha(mainScreen, color, head_verts)
    # Stop weird shapes when the arrow is shorter than arrow head
    # Unnecessary, since the arrow is at least one square long
    # if arrow.length() >= head_height:
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
    draw_polygon_alpha(mainScreen, color, body_verts)


def drawIdentifiers(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
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
                                    (i * CELL_SIZE[1]) +
                                    HALF_CELL_SIZE[1] - (text_size[1] // 2),
                                    BOARD_OFFSET[0], CELL_SIZE[1])
        identifier = mainScreen.blit(text, text_location)
        pygame.display.update(identifier)

    # Draw the Letter-Identifiers at the bottom
    for i in range(engine.DIMENSION[1]):
        text = font.render(gameState.alpha_identifiers[i], True, COLORS[6])
        text_size = (text.get_width(), text.get_height())
        text_location = pygame.Rect((i * CELL_SIZE[0]) + HALF_CELL_SIZE[0] - (text_size[0] // 2),
                                    IDENTIFIER_OFFSET[1] +
                                    (BOARD_OFFSET[1] - text_size[1]) // 2,
                                    CELL_SIZE[0], BOARD_OFFSET[1])
        identifier = mainScreen.blit(text, text_location)
        pygame.display.update(identifier)


def drawBoardCell(mainScreen: pygame.Surface, cell: tuple, cellSquare: pygame.Rect) -> None:
    """
    Draw a single Cell of the gameBoard on the mainScreen
    """
    pygame.draw.rect(mainScreen, COLORS[sum(cell) % 2], cellSquare)


def highlightCell(mainScreen: pygame.Surface, pos: tuple, color: tuple, alpha: int = 75) -> None:
    """
    Highlights a single cell at the index position 'pos' (x, y)
    and with the 'color' given as a tuple (R, G, B) and transperency 0 <= 'alpha' <= 255.
    """
    highlight = pygame.Surface(CELL_SIZE)
    highlight.set_alpha(alpha)
    highlight.fill(color)
    mainScreen.blit(highlight, (pos[0] * CELL_SIZE[0], pos[1] * CELL_SIZE[1]))


def circleCell(mainScreen: pygame.Surface, pos: tuple, color: tuple, alpha: int = 75):
    """
    Draw a transparent circle on the cell at index position 'pos' (x, y)
    """
    target_rect = pygame.Rect(pos[0] * CELL_SIZE[0], pos[1] * CELL_SIZE[1], *CELL_SIZE)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    shape_surf.set_alpha(alpha)
    pygame.draw.circle(shape_surf, color, HALF_CELL_SIZE, min(HALF_CELL_SIZE), 5)
    mainScreen.blit(shape_surf, target_rect)


def highlightLastMovedCell(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight the cell that is currently selected.
    """
    if not cell in holder.last_move:
        return
    highlightCell(mainScreen, cell, COLORS[9])


def highlightSelectedCell(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight the cell that is currently selected.
    """
    if cell != holder.selectedPiece.getPos():
        return
    highlightCell(mainScreen, cell, COLORS[3])


def highlightMoveOptions(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is valid for movement
    """
    if not cell in holder.options_move:
        return
    highlightCell(mainScreen, cell, COLORS[4])


def highlightAttackOptions(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is valid for attack
    """
    if not cell in holder.options_attack:
        return
    highlightCell(mainScreen, cell, COLORS[5])


def highlightMarkedCellSquare(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is marked
    """
    if not cell in holder.marked_cells_square:
        return
    highlightCell(mainScreen, cell, COLORS[2], 150)
        
        
def highlightMarkedCellCircle(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is marked
    """
    if not cell in holder.marked_cells_circle:
        return
    if cell in holder.marked_cells_square:
        return
    circleCell(mainScreen, cell, COLORS[2], 150)


def highlightHoveredCell(mainScreen: pygame.Surface, hoveredCell: tuple, cell: tuple) -> None:
    """
    highlight a cell if it's position is currently hovered above.
    """
    if not cell == hoveredCell:
        return
    highlightCell(mainScreen, cell, COLORS[1 - (sum(cell) % 2)])


def drawPiece(mainScreen: pygame.Surface, piece: Piece, cell: tuple) -> None:
    """
    draw a single piece.image on the mainScreen, including health- and damage-values
    """
    if not piece:
        return
    mainScreen.blit(piece.image,
                    pygame.Rect(cell[0] * CELL_SIZE[0] + IMAGE_OFFSET[0],
                                cell[1] * CELL_SIZE[1] + IMAGE_OFFSET[1],
                                *IMG_SIZE))
    if argparser.DEFAULT_MODE:
        return
    mainScreen.blit(holder.attack_icon, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]))
    font = pygame.font.SysFont("Verdana", int(16 * ((min(CELL_SIZE)/128))))
    mainScreen.blit(font.render(str(piece.damage), True, COLORS[6]),
                    (cell[0] * CELL_SIZE[0] + BOARD_OFFSET[0],
                        cell[1] * CELL_SIZE[1]))
    pygame.draw.rect(mainScreen, COLORS[2],
                     pygame.Rect(cell[0] * CELL_SIZE[0] + (IMAGE_OFFSET[0]//2),
                                 (cell[1] + 1) * CELL_SIZE[1] - (IMAGE_OFFSET[1]//2),
                                 (piece.health * (CELL_SIZE[0] - IMAGE_OFFSET[0]))//piece.maxHealth,
                                 IMAGE_OFFSET[1] // 3))
    font = pygame.font.SysFont("Verdana", int(10 * ((min(CELL_SIZE)/128))))
    text = font.render(str(piece.health), True, COLORS[6])
    text_size = (text.get_width(), text.get_height())
    text_location = pygame.Rect(cell[0] * CELL_SIZE[0] + (IMAGE_OFFSET[0]//2),
                                (cell[1] + 1) * CELL_SIZE[1] -
                                IMAGE_OFFSET[1] - text_size[1] // 2,
                                IMAGE_OFFSET[0]//2,
                                IMAGE_OFFSET[1]//2)
    mainScreen.blit(text, text_location)
    text = font.render(str(piece.maxHealth), True, COLORS[6])
    text_size = (text.get_width(), text.get_height())
    text_location = pygame.Rect((cell[0] + 1) * CELL_SIZE[0] - IMAGE_OFFSET[0] - text_size[0] // 2,
                                (cell[1] + 1) * CELL_SIZE[1] -
                                IMAGE_OFFSET[1] - text_size[1] // 2,
                                IMAGE_OFFSET[0]//2,
                                IMAGE_OFFSET[1]//2)
    mainScreen.blit(text, text_location)


def drawGameCell(mainScreen: pygame.Surface, gameState: engine.GameState, cell: tuple) -> None:
    """
    draw a single cell on the mainScreen, including all it's possible states.
    """
    if not (0 <= cell[0] < engine.DIMENSION[1]) or \
            not (0 <= cell[1] < engine.DIMENSION[0]):
        return
    cellSquare = pygame.Rect(cell[0] * CELL_SIZE[0],
                             cell[1] * CELL_SIZE[1],
                             *CELL_SIZE)
    drawBoardCell(mainScreen, cell, cellSquare)
    highlightLastMovedCell(mainScreen, cell)
    if holder.selectedPiece:
        highlightSelectedCell(mainScreen, cell)
        highlightMoveOptions(mainScreen, cell)
        highlightAttackOptions(mainScreen, cell)
    highlightMarkedCellSquare(mainScreen, cell)
    if holder.highlight_cells:
        highlightHoveredCell(mainScreen, getMouseCell(), cell)
    drawPiece(mainScreen, gameState.getPiece(cell), cell)
    highlightMarkedCellCircle(mainScreen, cell)
    pygame.display.update(cellSquare)


def drawWinner(mainScreen: pygame.Surface) -> None:
    """
    If a player has won this function will display the win-message
    on the 'mainScreen'
    """
    if not holder.winner:
        return
    font = pygame.font.SysFont("Verdana", int(64 * ((min(CELL_SIZE)/128))))
    text = font.render(holder.winner, True, COLORS[6])
    text_size = (text.get_width(), text.get_height())
    text_location = pygame.Rect(BOARD_SIZE[0] // 2 - text_size[0] // 2,
                                BOARD_SIZE[1] // 2 - text_size[1] // 2, *text_size)
    pygame.display.update(mainScreen.blit(text, text_location))
    font = pygame.font.SysFont("Verdana", int(32 * ((min(CELL_SIZE)/128))))
    text = font.render("Play Again (R)", True, COLORS[7])
    text_location = pygame.Rect(BOARD_SIZE[0] // 2 - text.get_width() // 2,
                                BOARD_SIZE[1] // 2 + text_size[1] // 2,
                                text.get_width(), text.get_height())
    pygame.display.update(mainScreen.blit(text, text_location))


def drawPlanningArrows(mainScreen: pygame.Surface) -> None:
    arrow_thickness = 2 * min(IMAGE_OFFSET)
    for arrow in holder.planning_arrows:
        drawArrow(mainScreen, arrow[0], arrow[1], COLORS[8],
                  arrow_thickness, 2 * arrow_thickness, arrow_thickness)


def clearPlanningArrows(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    # TODO: raytrace neccessary cells
    arrowCoveredCells = set()
    for from_pos, to_pos in holder.planning_arrows:
        from_pos_x, from_pos_y = from_pos
        to_pos_x, to_pos_y = to_pos
        from_pos_x //= CELL_SIZE[0]
        from_pos_y //= CELL_SIZE[1]
        to_pos_x //= CELL_SIZE[0]
        to_pos_y //= CELL_SIZE[1]
        for x in range(int(min(from_pos_x, to_pos_x)), int(max(from_pos_x, to_pos_x))+1):
            for y in range(int(min(from_pos_y, to_pos_y)), int(max(from_pos_y, to_pos_y))+1):
                arrowCoveredCells.add((x, y))
    for cell in arrowCoveredCells:
        drawGameCell(mainScreen, gameState, cell)


def clearPlanning(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    """
    clear Planning Cells and Arrows from the 'mainScreen'
    """
    # reset cell highlighting
    holder.highlight_cells = argparser.HIGHLIGHT_CELLS
    # Clear all previous rendered marked cells
    old_marks = holder.marked_cells_circle.copy()
    holder.marked_cells_square.clear()
    holder.marked_cells_circle.clear()
    for cell in old_marks:
        drawGameCell(mainScreen, gameState, cell)

    # clear all previous rendered arrows
    clearPlanningArrows(mainScreen, gameState)
    holder.planning_arrows.clear()


def renderGame(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    """
    draw every cell on the mainScreen.
    """
    drawIdentifiers(mainScreen, gameState)
    for x in product(range(engine.DIMENSION[1]), range(engine.DIMENSION[0])):
        drawGameCell(mainScreen, gameState, x)
    drawPlanningArrows(mainScreen)
    drawWinner(mainScreen)


def setLastMoveCells(gameState: engine.GameState) -> None:
    """
    get the last move starting and target cell.
    """
    holder.last_move = gameState.translateActionRepr(gameState.action_log.get(-1))


def drawPieceOptionsGen(mainScreen: pygame.Surface, pos: tuple, promoteOptions: list) -> None:
    """
    If a piece should be placed this function will draw the options on the
    cell at position 'pos', aswell as the hover-highlight effect for
    said options.
    """
    old_col, old_row = -1, -1
    cellPositions = [(p[0] * CELL_SIZE[0], p[1] * CELL_SIZE[1]) for _,p in promoteOptions]
    optionPositionOverall = pygame.Rect(*cellPositions[0],
                                        CELL_SIZE[0],
                                        CELL_SIZE[1] * len(promoteOptions))
    while True:
        col, row = getMouseCell()
        # only render the options, when the mouse is over another cell, and the cell is
        # in close proximity to the options
        if (col != old_col or row != old_row) and pos[0] - 1 <= col <= pos[0] + 1 and pos[1] - 1 <= row <= pos[1] + len(promoteOptions):
            for i, option in enumerate(promoteOptions):
                # draw board cell
                pygame.draw.rect(mainScreen, COLORS[(sum(pos) + i) % 2],
                                 pygame.Rect(*cellPositions[i], *CELL_SIZE))
                if (col == pos[0] and row == (pos[1] + i)):
                    # highlight
                    highlightCell(mainScreen, option[1], COLORS[3])
                # piece
                mainScreen.blit(option[0],
                            pygame.Rect(cellPositions[i][0] + IMAGE_OFFSET[0],
                                        cellPositions[i][1] + IMAGE_OFFSET[1],
                                        *IMG_SIZE))
                # circle option
                circleCell(mainScreen, (pos[0], pos[1] + i), COLORS[6], 200)
            pygame.display.update(optionPositionOverall)
        yield


def choosePieceOption(mainScreen: pygame.Surface, gameState: engine.GameState, pos: tuple, crazyPlace: bool = False) -> bool:
    """
    Takes over the main Loop, until the player has decided which piece to place.
    Returns a boolean in case the game is being quit, or the function is being aborted.
    The return value depends on the context!
    """
    currentPlayer = gameState.currentPlayer()
    if crazyPlace:
        availablePieces = gameState.getCrazyPlaceOptionsPieces()
        promoteOptions = list(set([piece._name for piece in availablePieces]))
        promoteOptions.sort()
        if len(promoteOptions) == 0:
            return PLACEPIECE_ABORTED
    else:
        promoteOptions = [PieceChar.BISHOP, PieceChar.KNIGHT,
                            PieceChar.QUEEN,  PieceChar.ROOK]
    
    pygame.display.set_mode(BOARD_SIZE, pygame.DOUBLEBUF) # disable resizing momentarily
    
    offsetPos = pos
    if (pos[1] + len(promoteOptions)) > engine.DIMENSION[0]:
        offsetPos = (pos[0], pos[1] - ((pos[1] + len(promoteOptions)) - engine.DIMENSION[0]))
    
    promoteOptionsDimensions = []
    for i, pieceChar in enumerate(promoteOptions):
        position = (offsetPos[0], offsetPos[1] + i)
        promoteOptionsDimensions.append([loadImage(currentPlayer+pieceChar, IMG_SIZE), position])
    
    piecePlaced = -1
    drawGen = drawPieceOptionsGen(mainScreen, offsetPos, promoteOptionsDimensions)
    while piecePlaced == -1:
        next(drawGen)
        pygame.time.delay(25)  # relieve the CPU a bit ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                piecePlaced = PLACEPIECE_QUIT
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    col, row = getMouseCell()
                    if (col == offsetPos[0]) and (offsetPos[1] <= row < offsetPos[1] + len(promoteOptions)):
                        gameState.placePiece(pos, promoteOptions[row-offsetPos[1]])
                        piecePlaced = PLACEPIECE_PLACED
                        if crazyPlace:
                            for piece in availablePieces:
                                if piece._name == promoteOptions[row-offsetPos[1]]:
                                    availablePieces.remove(piece)
                                    gameState.setCrazyPlaceOptionsPieces(availablePieces)
                                    break
                    elif crazyPlace: # if clicked somewhere else and we are not promoting -> abort
                        piecePlaced = PLACEPIECE_ABORTED
    pygame.display.set_mode(BOARD_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE) # reset resizablity
    
    # if we aborted the option to place a piece by clicking somewhere else
    # we need to re-render the entire screen, because we messed with
    # pygame.display
    if crazyPlace and piecePlaced == PLACEPIECE_ABORTED:
        renderGame(mainScreen, gameState)
    # otherwise it is sufficient to render the used cells, because
    # the turn is thereby finished and the screen will re-render anyway
    else:
        for i in range(len(promoteOptions)): # cleanup
            drawGameCell(mainScreen, gameState, (offsetPos[0], offsetPos[1] + i))
    return piecePlaced


def rescaleWindow(newWidth: int, newHeight: int, gameState: engine.GameState) -> None:
    """
    change all global size variables according to the rescaled window attributes.
    """
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
    CELL_SIZE = ((BOARD_SIZE[0] - BOARD_OFFSET[0]) // engine.DIMENSION[1],
                 (BOARD_SIZE[1] - BOARD_OFFSET[1]) // engine.DIMENSION[0])
    HALF_CELL_SIZE = (CELL_SIZE[0]//2, CELL_SIZE[1]//2)
    IDENTIFIER_OFFSET = (engine.DIMENSION[1] * CELL_SIZE[0],
                         engine.DIMENSION[0] * CELL_SIZE[1])
    IMG_SIZE = (int(CELL_SIZE[0] * 0.75),
                int(CELL_SIZE[1] * 0.75))
    IMAGE_OFFSET = (int(CELL_SIZE[0] * 0.125),
                    int(CELL_SIZE[1] * 0.125))

    holder.fps = fpsClock.FPS(
        argparser.MAX_FPS, BOARD_SIZE[0]-30-BOARD_OFFSET[0], 0)
    holder.attack_icon = loadImage("damage", BOARD_OFFSET)

    clearPieceImageCache()
    for piece in gameState.pieces:
        piece.loadImage(IMG_SIZE)

    for arrow in holder.planning_arrows:
        arrow[0][0] = (arrow[0][0] - (CELL_SIZE_OLD[0] // 2)
                       ) // CELL_SIZE_OLD[0]
        arrow[0][1] = (arrow[0][1] - (CELL_SIZE_OLD[1] // 2)
                       ) // CELL_SIZE_OLD[1]
        arrow[1][0] = (arrow[1][0] - (CELL_SIZE_OLD[0] // 2)
                       ) // CELL_SIZE_OLD[0]
        arrow[1][1] = (arrow[1][1] - (CELL_SIZE_OLD[1] // 2)
                       ) // CELL_SIZE_OLD[1]

        arrow[0][0] = arrow[0][0] * CELL_SIZE[0] + (CELL_SIZE[0] // 2)
        arrow[0][1] = arrow[0][1] * CELL_SIZE[1] + (CELL_SIZE[1] // 2)
        arrow[1][0] = arrow[1][0] * CELL_SIZE[0] + (CELL_SIZE[0] // 2)
        arrow[1][1] = arrow[1][1] * CELL_SIZE[1] + (CELL_SIZE[1] // 2)
        
    gameState.image_size = IMG_SIZE


def gameFinished(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    """
    we display the winning message and temporarily block mousepresses
    until the game is quit or restarted
    """
    holder.winner = gameState.playerWon()
    if holder.winner:
        pygame.event.set_blocked([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
        
        # update the old and new last move taken cells
        last_move_old = holder.last_move[:]
        setLastMoveCells(gameState)
        for cell in holder.last_move + last_move_old:
            drawGameCell(mainScreen, gameState, cell)
            
        # draw the game-finished message
        drawWinner(mainScreen)   


def nextTurn(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    if not holder.winner:
        # wait a short while, because instant board flip doesnt give the player enough
        # feedback, that his action was performed
        pygame.time.delay(250)
        # switch to the other player and re-render the entire board, because of possible
        # board flips
        gameState.nextTurn()
        
        setLastMoveCells(gameState)
        renderGame(mainScreen, gameState)


def newGame() -> engine.GameState:
    """
    Resets all values and starts/returns a new engine.GameState.
    """
    holder.selectedPiece, holder.winner = None, None
    holder.options_move, holder.options_attack = [], []
    holder.last_move = [(-1, -1), (-1, -1)]
    # new game is tarted so we allow mouse presses again
    pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
    return engine.GameState(IMG_SIZE)


def mainGUI():
    holder.highlight_cells = argparser.HIGHLIGHT_CELLS
    pygame.init()
    mainScreen = pygame.display.set_mode(
        BOARD_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE)
    # for performance reasons we block unnecessary events
    pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEWHEEL,
                              pygame.KEYUP, pygame.TEXTINPUT])
    pygame.display.set_icon(loadImage("blackp", (20, 20)))

    holder.fps = fpsClock.FPS(
        argparser.MAX_FPS, BOARD_SIZE[0]-30-BOARD_OFFSET[0], 0)
    gameState = newGame()
    holder.attack_icon = loadImage("damage", BOARD_OFFSET)
    marked_old = (-1, -1)
    
    # isPlanning = 0 -> not planning -> highlight cells
    # isPlanning = 1 -> is planning -> remove last cell highlight
    # isPlanning = 2 -> is planning -> don't highlight cells
    isPlanning = 0
    mouseHover_old = (-1, -1)

    # first time rendering of the whole board
    renderGame(mainScreen, gameState)

    running = True
    while running:
        pygame.display.set_caption('Chess to the Death ' + holder.fps.getFps())

        # highlight cell at mouse position and re-render
        # cell at previous mouse position
        if holder.highlight_cells and not holder.winner:
            mouseHover = getMouseCell()
            if isPlanning == 1 and mouseHover != mouseHover_old:
                drawGameCell(mainScreen, gameState, mouseHover_old)
                holder.highlight_cells = False
                isPlanning = 2
            elif isPlanning == 0:
                drawGameCell(mainScreen, gameState, mouseHover)
                drawGameCell(mainScreen, gameState, mouseHover_old)
            mouseHover_old = mouseHover
        pygame.time.delay(25)  # relieve the CPU a bit ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Log:")
                print(gameState.action_log)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseHover = getMouseCell()
                # primary mouse button (left) or middle mouse button
                if event.button == 1 or (event.button == 2 and argparser.CRAZY_MODE):
                    # reset planning
                    isPlanning = 0
                    clearPlanning(mainScreen, gameState)
                # if the secondary (right) mouse button is pressed down we save the location
                elif event.button == 3:
                    # planning begins
                    isPlanning = 1
                    marked_old = mouseHover
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                     # see if there is a piece at the clicked position
                    piece = gameState.getPiece(mouseHover)
                    print("Selected:", piece, mouseHover)
                    # if it is a valid piece of the current team, we can select it
                    if piece and gameState.selectablePiece(piece):
                        # if it was previously selected we deselect it
                        if piece == holder.selectedPiece:
                            piece = None
                        options_move_old, options_attack_old = holder.options_move, holder.options_attack
                        piece_old = holder.selectedPiece
                        holder.selectedPiece = piece
                        holder.options_move, holder.options_attack = gameState.getOptions(piece)
                        # render all optional actions and re-render all option actions from the previous selection
                        for cell in options_move_old + options_attack_old + holder.options_move + holder.options_attack:
                            drawGameCell(mainScreen, gameState, cell)
                        if piece:  # render new position
                            drawGameCell(mainScreen, gameState, piece.getPos())
                        if piece_old:  # re-render old position
                            drawGameCell(mainScreen, gameState, piece_old.getPos())
                    # if there already is a piece selected and now we clicked an empty piece or an empty cell
                    elif holder.selectedPiece:
                        # backup old piece and action options, for later re-rendering
                        piece_old = holder.selectedPiece
                        options_move_old, options_attack_old = holder.options_move, holder.options_attack
                        piecePos_old = piece_old.getPos()

                        # take the action, this will return the type of action taken or if the game is finished or
                        # if a pawn can be promoted
                        action = gameState.action(
                            holder.selectedPiece, mouseHover, holder.options_move, holder.options_attack)
                        if action:
                            holder.options_move, holder.options_attack = [], []
                            holder.selectedPiece = None

                            # we re-render the old action options and the old piece position
                            for cell in options_move_old + options_attack_old:
                                drawGameCell(mainScreen, gameState, cell)
                            drawGameCell(mainScreen, gameState, piecePos_old)

                            # if the game is finished (draw, stalemate, mate ...)
                            if action == Outcome.GAME_FINISHED:
                                gameFinished(mainScreen, gameState)
                            # if a pawn can be promoted
                            elif action == Outcome.PAWN_PROMOTION:
                                print("Choose Pawn Promotion...")
                                # we let the player choose the promotion
                                piecePlaced = choosePieceOption(mainScreen, gameState, mouseHover)
                                if piecePlaced == PLACEPIECE_PLACED:
                                    print("Pawn promoted!")
                                    gameFinished(mainScreen, gameState)
                                running = not (piecePlaced == PLACEPIECE_QUIT)
                            if running:
                                nextTurn(mainScreen, gameState)
                elif event.button == 2 and argparser.CRAZY_MODE:
                    if gameState.restrictedCrazyPlace(mouseHover):
                        piecePlaced = choosePieceOption(mainScreen, gameState, mouseHover, True)
                        if piecePlaced == PLACEPIECE_PLACED:
                            gameFinished(mainScreen, gameState)
                            nextTurn(mainScreen, gameState)
                        running = not (piecePlaced == PLACEPIECE_QUIT)
                elif event.button == 3:
                    mouseHover = getMouseCell()
                    mouseHover = (min(mouseHover[0], engine.DIMENSION[1]-1),
                                  min(mouseHover[1], engine.DIMENSION[0]-1))
                    marked_old = (min(marked_old[0], engine.DIMENSION[1]-1),
                                  min(marked_old[1], engine.DIMENSION[0]-1))

                    if mouseHover == marked_old:
                        if mouseHover in holder.marked_cells_circle:
                            holder.marked_cells_square.add(mouseHover)
                        holder.marked_cells_circle.add(mouseHover)
                        drawGameCell(mainScreen, gameState, mouseHover)
                        clearPlanningArrows(mainScreen, gameState)
                        drawPlanningArrows(mainScreen)
                    else:
                        newArrow = (pygame.Vector2(marked_old[0] * CELL_SIZE[0] + CELL_SIZE[0]//2,
                                                   marked_old[1] * CELL_SIZE[1] + CELL_SIZE[1]//2),
                                    pygame.Vector2(mouseHover[0] * CELL_SIZE[0] + CELL_SIZE[0]//2,
                                                   mouseHover[1] * CELL_SIZE[1] + CELL_SIZE[1]//2))
                        # if not newArrow in holder.planning_arrows:
                        holder.planning_arrows.append(newArrow)
                        arrow_thickness = 2 * min(IMAGE_OFFSET)
                        drawArrow(mainScreen, newArrow[0], newArrow[1], COLORS[8],
                                  arrow_thickness, 2 * arrow_thickness, arrow_thickness)
            elif event.type == pygame.KEYDOWN and holder.winner:
                if pygame.key.name(event.key) == 'r':
                    # restart the game if 'r' is pressed,
                    # new gameengine and refresh of entire board
                    print("Log:")
                    print(gameState.action_log)
                    print("Restarting...")
                    gameState = newGame()
                    renderGame(mainScreen, gameState)
            elif event.type == pygame.VIDEORESIZE:
                # if the window has been rescaled/resized we need to update all global variables
                # according to the new size
                rescaleWindow(event.w, event.h, gameState)
                mainScreen = pygame.display.set_mode(BOARD_SIZE, pygame.DOUBLEBUF | pygame.RESIZABLE)
                # then we render everything again
                renderGame(mainScreen, gameState)
            elif event.type == pygame.WINDOWRESTORED:  # handles window minimising/maximising
                renderGame(mainScreen, gameState)
    pygame.quit()
    print("GoodBye!")
