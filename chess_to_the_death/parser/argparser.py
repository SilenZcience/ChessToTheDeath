import argparse
from sys import exit as sysexit
from datetime import datetime
from os import path
import chess_to_the_death.util.config as config
from chess_to_the_death.web.UpdateChecker import printUpdateInformation
from chess_to_the_death import __version__, __sysversion__, __author__

MAX_FPS = 20
HIGHLIGHT_CELLS = True
FLIP_BOARD = True
RANDOM_VALUES = False
DEFAULT_MODE = False
CRAZY_MODE = False
STARTING_POSITION = None

class ArgsHandler:
    params: argparse.Namespace = None
    
    def __init__(self, file: str):
        self.file = file
        self.workingDir = path.dirname(path.realpath(self.file))
        self.parseArgs()
        self.translateArgs()

    def getParams(self) -> argparse.Namespace:
        return self.params

    def parseArgs(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--version", action="store_const", default=False,
                            const=True, dest="version", help="show program's version number and exit")
        parser.add_argument("-fps", "--fps", action="store", default=20, type=int,
                            dest="fps", help="set max fps (a lower value will improve performance)")
        parser.add_argument("-nohighlight", action="store_const", default=True, dest="highlight",
                            const=False, help="disable cell-highlighting on mouse hover")
        parser.add_argument("-noflip", action="store_const", default=True, dest="flip",
                            const=False, help="disable board flipping")
        parser.add_argument("-random", action="store_const", default=False, dest="random",
                            const=True, help="randomize the health and damage values of all pieces.")
        parser.add_argument("-default", action="store_const", default=False, dest="default",
                            const=True, help="play the default chess variant.")
        parser.add_argument("-crazy", action="store_const", default=False, dest="crazy",
                            const=True, help="play the crazyhouse chess variant.")
        parser.add_argument("-pos", action="store", default=None, dest="position",
                            help="FEN starting position")
        
        self.params = parser.parse_args()
    
    def translateArgs(self) -> None:
        global MAX_FPS
        global HIGHLIGHT_CELLS
        global FLIP_BOARD
        global RANDOM_VALUES
        global DEFAULT_MODE
        global CRAZY_MODE
        global STARTING_POSITION
        if getattr(self.params, 'version'):
            self._showVersion()
            sysexit(0)
        MAX_FPS = getattr(self.params, 'fps')
        HIGHLIGHT_CELLS = getattr(self.params, 'highlight')
        FLIP_BOARD = getattr(self.params, 'flip')
        RANDOM_VALUES = getattr(self.params, 'random')
        DEFAULT_MODE = getattr(self.params, 'default')
        CRAZY_MODE = getattr(self.params, 'crazy')
        STARTING_POSITION = getattr(self.params, 'position')
        config.generateBoardFromFEN(STARTING_POSITION, CRAZY_MODE)
        
    def _showVersion(self) -> None:
        print()
        print("------------------------------------------------------------")
        print(f"ChessToTheDeath {__version__} - from {self.workingDir}")
        print("------------------------------------------------------------")
        print()
        print(f"Python: \t{__sysversion__}")  # sys.version
        print(f"Build time: \t{datetime.fromtimestamp(path.getctime(path.realpath(__file__)))} CET")
        print(f"Author: \t{__author__}")
        printUpdateInformation("ChessToTheDeath", __version__)
