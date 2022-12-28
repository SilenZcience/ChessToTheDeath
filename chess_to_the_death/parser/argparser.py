import argparse
from sys import exit as sysexit
from datetime import datetime
from os import path
from chess_to_the_death.web.UpdateChecker import printUpdateInformation
from chess_to_the_death import __version__, __sysversion__, __author__


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
        parser.add_argument("-default", action="store_const", default=False, dest="default",
                            const=True, help="play the default chess variant.")
        
        self.params = parser.parse_args()
    
    def translateArgs(self) -> None:
        if getattr(self.params, 'version'):
            self._showVersion()
            sysexit(0)
        
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

