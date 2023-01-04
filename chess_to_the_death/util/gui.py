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

COLORS = [(230, 230, 230, 255), #"#E6E6E6" -> WHITE / CELL + HOVER
          ( 32,  33,  36, 255), #"#202124" -> DARK_GRAY / CELL + HOVER
          (255,   0,   0, 255), #"#FF0000" -> RED / HEALTH
          (  0,   0, 255, 255), #"#0000FF" -> BLUE / SELECTED
          (  0, 255,   0, 255), #"#00FF00" -> GREEN / MOVABLE
          (255,   0,   0, 255), #"#FF0000" -> RED / ATTACKABLE
          ( 46, 149, 153, 255), #"#2E9599" -> TEAL / TEXT
          (  0,   0,   0, 255), #"#000000" -> BLACK / REDO
          (255, 165,   0, 150), #"#FFA500" -> ORANGE / PLANNING_ARROWS
          (218, 112, 214, 255)] #"#DA70D6" -> PINK / LAST MOVE

# define a holder object to hold variables bundled in a global spectrum
# and instantiate it
class Holder:
    selectedCell: Piece = None
    winner: str = ''
    options_move, options_attack = [], []
    last_move = []
    marked_cells = set()
    planning_arrows = []
    attack_icon: pygame.Surface = None
    fps: fpsClock = None

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


def draw_polygon_alpha(mainScreen, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [
                        (x - min_x, y - min_y) for x, y in points])
    polyBlit = mainScreen.blit(shape_surf, target_rect)
    pygame.display.update(polyBlit)


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
    translation = pygame.Vector2(
        0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    draw_polygon_alpha(mainScreen, color, head_verts)
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
        draw_polygon_alpha(mainScreen, color, body_verts)


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


def highlightCell(mainScreen: pygame.Surface, pos: tuple, size: tuple, color: tuple, alpha: int = 75) -> None:
    """
    Highlights a single cell at the coordinates 'pos' (x, y), with 'size' (w, h) 
    and with the 'color' given as a tuple (R, G, B) and transperency 0 <= 'alpha' <= 255.
    """
    highlight = pygame.Surface(size)
    highlight.set_alpha(alpha)
    highlight.fill(color)
    mainScreen.blit(highlight, pos)


def highlightLastMovedCell(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight the cell that is currently selected.
    """
    if not cell in holder.last_move:
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[9])


def highlightSelectedCell(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight the cell that is currently selected.
    """
    if cell != holder.selectedCell.getPos():
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[3])


def highlightMoveOptions(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is valid for movement
    """
    if not cell in holder.options_move:
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[4])


def highlightAttackOptions(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is valid for attack
    """
    if not cell in holder.options_attack:
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[5])


def highlightMarkedCell(mainScreen: pygame.Surface, cell: tuple) -> None:
    """
    highlight a cell if it's position is marked
    """
    if not cell in holder.marked_cells:
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[2], 150)


def highlightHoveredCell(mainScreen: pygame.Surface, hoveredCell: tuple, cell: tuple) -> None:
    """
    highlight a cell if it's position is currently hovered above.
    """
    if not cell == hoveredCell:
        return
    highlightCell(mainScreen, (cell[0] * CELL_SIZE[0], cell[1] * CELL_SIZE[1]),
                  CELL_SIZE, COLORS[1 - (sum(cell) % 2)])


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
    if holder.selectedCell:
        highlightSelectedCell(mainScreen, cell)
        highlightMoveOptions(mainScreen, cell)
        highlightAttackOptions(mainScreen, cell)
    highlightMarkedCell(mainScreen, cell)
    if argparser.HIGHLIGHT_CELLS:
        highlightHoveredCell(mainScreen, getMouseCell(), cell)
    drawPiece(mainScreen, gameState.getPiece(cell), cell)
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


def renderGame(mainScreen: pygame.Surface, gameState: engine.GameState) -> None:
    """
    draw every cell on the mainScreen.
    """
    drawIdentifiers(mainScreen, gameState)
    for x in product(range(engine.DIMENSION[1]), range(engine.DIMENSION[0])):
        drawGameCell(mainScreen, gameState, x)
    drawPlanningArrows(mainScreen)
    drawWinner(mainScreen)


def setLastMoveCells(gameState: engine.GameState):
    holder.last_move = gameState.translateActionRepr(gameState.action_log.get(-1))


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
        highlightedArea = highlightCell(mainScreen, ((col//2) * CELL_SIZE[0] + (HALF_CELL_SIZE[0] * (col % 2)),
                                                     (row//2) * CELL_SIZE[1] + (HALF_CELL_SIZE[1] * (row % 2))),
                                        HALF_CELL_SIZE, COLORS[3])
        pygame.display.update(highlightedArea)
    for options in promoteOptions:
        for option in options:
            promoteOption = mainScreen.blit(option[0], pygame.Rect(*option[1]))
            pygame.display.update(promoteOption)


def choosePromoteOptions(mainScreen: pygame.Surface, gameState: engine.GameState, piece: Piece) -> bool:
    """
    Takes over the main Loop, until the player has decided to which piece the pawn
    should be promoted.
    Returns a boolean in case the game is being quit.
    """
    currentPlayer = gameState.currentPlayer()
    promoteOptions = [[PieceChar.KNIGHT, PieceChar.BISHOP],
                      [PieceChar.ROOK, PieceChar.QUEEN]]
    promoteOptionsDimensions = [[(loadImage(currentPlayer+PieceChar.KNIGHT, HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0],
                                   piece.cell_row * CELL_SIZE[1],
                                   *HALF_CELL_SIZE)),
                                 (loadImage(currentPlayer+PieceChar.BISHOP, HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0] + HALF_CELL_SIZE[0],
                                     piece.cell_row * CELL_SIZE[1],
                                     *HALF_CELL_SIZE))],
                                [(loadImage(currentPlayer+PieceChar.ROOK, HALF_CELL_SIZE),
                                  (piece.cell_col * CELL_SIZE[0],
                                    piece.cell_row *
                                   CELL_SIZE[1] + HALF_CELL_SIZE[1],
                                    *HALF_CELL_SIZE)),
                                 (loadImage(currentPlayer+PieceChar.QUEEN, HALF_CELL_SIZE),
                                    (piece.cell_col * CELL_SIZE[0] + HALF_CELL_SIZE[0],
                                     piece.cell_row *
                                     CELL_SIZE[1] + HALF_CELL_SIZE[1],
                                     *HALF_CELL_SIZE))]]
    
    while True:
        drawPromoteOptions(mainScreen, piece, promoteOptionsDimensions)
        pygame.time.delay(25)  # relieve the CPU a bit ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                col, row = getMouseCell(True)
                if (col//2 == piece.cell_col) and (
                        row//2 == piece.cell_row):
                    col -= (2*piece.cell_col)
                    row -= (2*piece.cell_row)
                    gameState.promotePiece(piece, promoteOptions[row][col])
                    return True


def rescaleWindow(newWidth: int, newHeight: int, gameState: engine.GameState):
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


def newGame() -> engine.GameState:
    """
    Resets all values and starts/returns a new engine.GameState.
    """
    holder.selectedCell, holder.winner = None, None
    holder.options_move, holder.options_attack = [], []
    holder.last_move = [(-1, -1), (-1, -1)]
    # new game is tarted so we allow mouse presses again
    pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
    return engine.GameState(IMG_SIZE)


def mainGUI():
    
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
    # for performance reasons and avoidance of visual glitches we disable
    # cell hover highlighting during planning (arrows, marks)
    # we backup the original HIGHLIGHT_CELLS parameter.
    HIGHLIGHT_CELLS = argparser.HIGHLIGHT_CELLS
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
        if argparser.HIGHLIGHT_CELLS and not holder.winner:
            mouseHover = getMouseCell()
            if isPlanning == 1 and mouseHover != mouseHover_old:
                drawGameCell(mainScreen, gameState, mouseHover_old)
                argparser.HIGHLIGHT_CELLS = False
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
                # primary mouse button (left)
                if event.button == 1:
                    # reset planning and cell highlighting
                    isPlanning = 0
                    argparser.HIGHLIGHT_CELLS = HIGHLIGHT_CELLS
                    # Clear all previous rendered marked cells
                    old_marks = holder.marked_cells.copy()
                    holder.marked_cells.clear()
                    for cell in old_marks:
                        drawGameCell(mainScreen, gameState, cell)

                    # clear all previous rendered arrows
                    clearPlanningArrows(mainScreen, gameState)
                    holder.planning_arrows.clear()

                    # see if there is a piece at the clicked position
                    piece = gameState.getPiece(mouseHover)
                    print("Selected:", piece, mouseHover)
                    # if it is a valid piece of the current team, we can select it
                    if piece and gameState.selectablePiece(piece):
                        # if it was previously selected we deselect it
                        if piece == holder.selectedCell:
                            piece = None
                        options_move_old, options_attack_old = holder.options_move, holder.options_attack
                        piece_old = holder.selectedCell
                        holder.selectedCell = piece
                        holder.options_move, holder.options_attack = gameState.getOptions(piece)
                        # render all optional actions and re-render all option actions from the previous selection
                        for cell in options_move_old + options_attack_old + holder.options_move + holder.options_attack:
                            drawGameCell(mainScreen, gameState, cell)
                        if piece:  # render new position
                            drawGameCell(mainScreen, gameState, piece.getPos())
                        if piece_old:  # re-render old position
                            drawGameCell(mainScreen, gameState, piece_old.getPos())
                    # if there already is a piece selected and now we clicked an empty piece or an empty cell
                    elif holder.selectedCell:
                        # backup old piece and action options, for later re-rendering
                        piece_old = holder.selectedCell
                        options_move_old, options_attack_old = holder.options_move, holder.options_attack
                        piecePos_old = piece_old.getPos()

                        # take the action, this will return the type of action taken or if the game is finished or
                        # if a pawn can be promoted
                        action = gameState.action(
                            holder.selectedCell, mouseHover, holder.options_move, holder.options_attack)
                        if action:
                            holder.options_move, holder.options_attack = [], []
                            holder.selectedCell = None

                            # we re-render the old action options and the old piece position
                            for cell in options_move_old + options_attack_old:
                                drawGameCell(mainScreen, gameState, cell)
                            drawGameCell(mainScreen, gameState, piecePos_old)

                            # if the game is finished (draw, stalemate, mate ...)
                            if action == Outcome.GAME_FINISHED:
                                # we display the winning message and temporarily block mousepresses
                                # until the game is quit or restarted
                                holder.winner = gameState.playerWon()
                                pygame.event.set_blocked([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
                                
                                # update the old and new last move taken cells
                                last_move_old = holder.last_move[:]
                                setLastMoveCells(gameState)
                                for cell in holder.last_move + last_move_old:
                                    drawGameCell(mainScreen, gameState, cell)
                                    
                                # draw the game-finished message
                                drawWinner(mainScreen)
                            # if a pawn can be promoted
                            elif action == Outcome.PAWN_PROMOTION:
                                print("Choose Pawn Promotion...")
                                # we let the player choose the promotion
                                running = choosePromoteOptions(mainScreen, gameState, piece_old)
                                print("Pawn promoted!")
                                # render the new promoted piece
                                drawGameCell(mainScreen, gameState, mouseHover)
                            if running and not holder.winner:
                                # wait a short while, because instant board flip doesnt give the player enough
                                # feedback, that his action was performed
                                pygame.time.delay(250)
                                # switch to the other player and re-render the entire board, because of possible
                                # board flips
                                gameState.nextTurn()
                                
                                setLastMoveCells(gameState)
                                renderGame(mainScreen, gameState)
                # if the secondary (right) mouse button is pressed down we save the location
                elif event.button == 3:
                    marked_old = mouseHover
                    # planning begins
                    isPlanning = 1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    mouseHover = getMouseCell()
                    mouseHover = (min(mouseHover[0], engine.DIMENSION[1]-1),
                                  min(mouseHover[1], engine.DIMENSION[0]-1))
                    marked_old = (min(marked_old[0], engine.DIMENSION[1]-1),
                                  min(marked_old[1], engine.DIMENSION[0]-1))

                    if mouseHover == marked_old:
                        holder.marked_cells.add(mouseHover)
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
                        planningBlit = drawArrow(mainScreen, newArrow[0], newArrow[1], COLORS[8],
                                                 arrow_thickness, 2 * arrow_thickness, arrow_thickness)
                        pygame.display.update(planningBlit)
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
    pygame.quit()
    print("GoodBye!")
