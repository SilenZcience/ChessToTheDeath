from chess_to_the_death.parser.argparser import ArgsHandler
from chess_to_the_death.util.gui import mainGUI

if __name__ == '__main__':
    argsHandler = ArgsHandler(__file__)
    mainGUI(argsHandler.getParams())
