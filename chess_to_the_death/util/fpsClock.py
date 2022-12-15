import pygame


class FPS:
    text: pygame.Surface = None

    def __init__(self, fps, x, y):
        self.fps = fps
        self.pos = (x, y)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Verdana', 14)

    def render(self, screen: pygame.Surface) -> None:
        """
        takes a pygame.Surface mainscreen and renders the current
        fps on the initialized x,y coordinates.
        """
        self.clock.tick(self.fps)
        self.text = self.font.render(
            str(int(self.clock.get_fps())), True, (255, 255, 255))
        screen.blit(self.text, self.pos)
