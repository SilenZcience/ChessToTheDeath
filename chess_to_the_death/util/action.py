import numpy as np

class ActionLog:
    actions = []
    def add(self, board: np.ndarray, from_col: int, from_row: int, to_col: int, to_row: int, action: str):
        self.actions.append(Action(board, from_col, from_row, to_col, to_row, action))
        
    def get(self, index: int):
        return self.actions[index]
    
    def getPrintActionString(self, actionLogIndex: int = -1, color: str = '32') -> str:
        action = self.get(actionLogIndex)
        actionRepr = "\x1b[" + color + "m"
        actionRepr += str(action)
        actionRepr += "\x1b[m"
        actionRepr += "\n"
        return actionRepr
    
    def printAction(self, actionLogIndex: int = -1, color: str = '32') -> None:
        """
        Print the last action taken ANSI-colored to the console.
        """
        print(self.getPrintActionString(actionLogIndex, color))
        
    def __repr__(self) -> str:
        return ''.join([self.getPrintActionString(i, '33') for i in range(len(self.actions))])

class Action:
    def __init__(self, board: np.ndarray, from_col: str, from_row: str, to_col: str, to_row: str, action: str) -> None:
        self.board = board.copy()
        self.from_col = from_col
        self.from_row = from_row
        self.to_col = to_col
        self.to_row = to_row
        self.action = action
        
    def __repr__(self) -> str:
        return self.from_col + self.from_row + '-' + self.to_col + self.to_row + ' ' + self.action
        