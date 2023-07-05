import pygame
import numpy as np

from view.windows import Window


class WindowView:
    def __init__(self):
        self.windows = []

    def add_window(self, size, title, object=None):
        pos = (100 + len(self.windows) * 5, 100 + len(self.windows) * 5)
        self.windows.append(Window(size, pos, title, object))

    def handle_window_collision(self, mouse_position):
        for window in reversed(self.windows):
            if window.is_closing(mouse_position):
                self.windows.remove(window)

    def drag_window(self, mouse_position, relative_movement):
        for window in reversed(self.windows):
            if window.is_dragged(mouse_position):
                window.drag(window.pos + relative_movement)

    def draw_windows(self, surface: pygame.Surface):
        if len(self.windows) > 0:
            for window in self.windows:
                window.draw(surface, self)
