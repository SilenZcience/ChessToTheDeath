import numpy as np

class Action:
    def __init__(self, from_col: str, from_row: str, to_col: str, to_row: str, action: str) -> None:
        """
        from_col and to_col expect a char like 'A', 'B', ...
        from_row and to_row expect a char like '1', '2', ...
        """
        self.from_col = from_col
        self.from_row = from_row
        self.to_col = to_col
        self.to_row = to_row
        self.action = action
        
    def __repr__(self) -> str:
        return self.from_col + self.from_row + '-' + self.to_col + self.to_row + ' ' + self.action

class ActionLog:
    def __init__(self) -> None:
        self.actions = []
        self.boards = []
    
    def add(self, board: np.ndarray, from_col: str, from_row: str, to_col: str, to_row: str, action: str) -> None:
        """
        from_col and to_col expect a char like 'A', 'B', ...
        from_row and to_row expect a char like '1', '2', ...
        add an action to the log by saving the from- and to-position of the action taken aswell
        as the entire board
        """
        self.boards.append(board.copy())
        self.actions.append(Action(from_col, from_row, to_col, to_row, action))
        
    def get(self, index: int) -> Action:
        """
        return the action at log position 'index'
        """
        return self.actions[index]
    
    def getPrintActionString(self, actionLogIndex: int = -1, color: str = '32') -> str:
        """
        generate a string to represent an action
        """
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
        