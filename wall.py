import pygame


class Wall:
    def __init__(self, LEFT, TOP, WIDTH, HEIGHT, COLOR):
        self.screen = pygame.display.get_surface()
        self.left = LEFT
        self.top = TOP
        self.width = WIDTH
        self.height = HEIGHT
        self.object = pygame.Rect(LEFT, TOP, WIDTH, HEIGHT)
        self.color = COLOR
        self.draw()

    def draw(self):
        pygame.draw.rect(self.screen, self.color,
                         (self.left, self.top, self.width, self.height))

    def getLT(self):
        return self.left, self.top

    def getRT(self):
        return self.left + self.width, self.top

    def getLD(self):
        return self.left, self.top + self.height

    def getRD(self):
        return self.left + self.width, self.top + self.height
