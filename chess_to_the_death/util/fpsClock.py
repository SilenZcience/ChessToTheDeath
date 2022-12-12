import pygame


class FPS:
    text = ""

    def __init__(self, fps, x, y):
        self.fps = fps
        self.pos = (x, y)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Verdana', 14)

    def render(self, screen):
        self.clock.tick(self.fps)
        self.text = self.font.render(
            str(int(self.clock.get_fps())), True, (255, 255, 255))
        screen.blit(self.text, self.pos)
