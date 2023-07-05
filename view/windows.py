import pygame
import pygame.font

pygame.font.init()

FILL_COLOR = pygame.Color(210, 210, 210)
HEADER_COLOR = pygame.Color(160, 160, 160)

font = pygame.font.SysFont("Arial", 12)
close_icon = pygame.image.load("assets/close.png")


class Window:
    def __init__(self, size, pos, title, object=None):
        self.width = size[0]
        self.height = size[1]
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        self.title = title
        self.object = object

    def drag(self, pos):
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

    def get_header_rect(self):
        return pygame.Rect(
            self.pos[0] + 1, self.pos[1] + 1, self.width - 19, 16
        ), pygame.Rect((self.pos[0] + self.width - 17), self.pos[1] + 1, 16, 16)

    def get_header_info(self):
        text_surface = font.render(self.title, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = self.get_header_rect()[0].center
        return text_surface, text_rect

    def is_closing(self, pos):
        if self.get_header_rect()[1].collidepoint(pos):
            return True

    def is_dragged(self, pos):
        if self.get_header_rect()[0].collidepoint(pos):
            return True

    def draw(self, surface: pygame.Surface, view):
        header, close_icon_rect = self.get_header_rect()
        text_surface, text_rect = self.get_header_info()

        pygame.draw.rect(surface, FILL_COLOR, self.rect)
        pygame.draw.rect(surface, HEADER_COLOR, header)
        pygame.draw.rect(surface, HEADER_COLOR, close_icon_rect)

        surface.blit(text_surface, text_rect)
        surface.blit(close_icon, close_icon_rect)
