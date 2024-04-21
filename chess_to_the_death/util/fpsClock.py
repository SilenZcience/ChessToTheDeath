import pygame


class FPS:
    text: pygame.Surface = None

    def __init__(self, fps, x, y):
        self.fps = fps
        self.pos = (x, y)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Verdana', 14)

    def getFps(self) -> str:
        """
        ticks the pygame.time.Clock and returns the current fps as string
        """
        self.clock.tick(self.fps)
        return str(int(self.clock.get_fps()))
