from chess_to_the_death.parser.argparser import ArgsHandler
from chess_to_the_death.util.gui import mainGUI

if __name__ == '__main__':
    try:
        ArgsHandler(__file__)
        mainGUI()
    except KeyboardInterrupt:
        print("GoodBye!")
