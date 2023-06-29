import pygame
import numpy as np

key_state = {}

pan_speed = 10
zoom_speed = 0.025


def clamp(value, value_max, value_min):
    return max(min(value, value_max), value_min)


def handle_events():
    global key_state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        elif event.type == pygame.KEYDOWN:
            key_state[event.key] = True
        elif event.type == pygame.KEYUP:
            key_state[event.key] = False

    return key_state


def handle_view_controls(view):
    key_state = handle_events()
    if key_state.get(pygame.K_LEFT):
        view.position[0] += pan_speed / view.zoom
    if key_state.get(pygame.K_RIGHT):
        view.position[0] -= pan_speed / view.zoom
    if key_state.get(pygame.K_UP):
        view.position[1] += pan_speed / view.zoom
    if key_state.get(pygame.K_DOWN):
        view.position[1] -= pan_speed / view.zoom
    if key_state.get(pygame.K_PLUS):
        view.zoom = view.zoom + zoom_speed
    if key_state.get(pygame.K_MINUS):
        view.zoom = view.zoom - zoom_speed


class MapView:
    def __init__(self, map_size: list):
        self.position = [640, 360]
        self.offset = pygame.display.get_window_size()
        self.zoom = 1.0
        self.map_size = map_size

    def clamp(self):
        self.zoom = clamp(
            self.zoom, 2.2, max(self.offset[i] / self.map_size[i] for i in range(2))
        )
        self.position[0] = clamp(
            self.position[0],
            self.map_size[0] / 2 * self.zoom,
            -self.map_size[0] / 2 * self.zoom + self.offset[0],
        )
        self.position[1] = clamp(
            self.position[1],
            self.map_size[1] / 2 * self.zoom,
            -self.map_size[1] / 2 * self.zoom + self.offset[1],
        )

    def screen_coordinates(self, coordinates: np.ndarray) -> np.ndarray:
        return coordinates * self.zoom + self.position
