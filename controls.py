import pygame
import numpy as np
import nodes
from environment import Map


pan_speed = 10
zoom_speed = 0.025
mouse_button_pressed = False


def clamp(value, value_max, value_min):
    return max(min(value, value_max), value_min)


def handle_view_controls(view, key_state):
    """
    Handles the view controls.
    """
    global pan_speed, zoom_speed

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


def handle_user_input(view):
    global mouse_button_pressed

    # Using pygame, realize when a mouse button is pressed and released
    if pygame.mouse.get_pressed()[0] and not mouse_button_pressed:
        mouse_button_pressed = True
        view.handle_node_collision()
    elif not pygame.mouse.get_pressed()[0] and mouse_button_pressed:
        mouse_button_pressed = False


class MapView:
    """
    A class to represent the view of the map.

    Attributes:
        position (list): The position of the view.
        zoom (float): The zoom of the view.
        map_size (list): The size of the map.
    """

    def __init__(self, map: Map):
        self.position = [640, 360]
        self.zoom = 1.0
        self.cursor_position = np.array([0, 0])
        self.map = map

    def clamp(self):
        """
        Clamps the view to the map.
        """
        window_size = pygame.display.get_window_size()
        self.zoom = clamp(
            self.zoom, 2.2, max(window_size[i] / self.map.size[i] for i in range(2))
        )
        self.position[0] = clamp(
            self.position[0],
            self.map.size[0] / 2 * self.zoom,
            -self.map.size[0] / 2 * self.zoom + window_size[0],
        )
        self.position[1] = clamp(
            self.position[1],
            self.map.size[1] / 2 * self.zoom,
            -self.map.size[1] / 2 * self.zoom + window_size[1],
        )

    def screen_coordinates(self, coordinates: np.ndarray) -> np.ndarray:
        """
        Converts coordinates from the map to the screen.
        """
        return coordinates * self.zoom + self.position

    def get_cursor_position(self):
        self.cursor_position = np.array(pygame.mouse.get_pos())
        return self.cursor_position

    def handle_node_collision(self):
        mouse_position = self.get_cursor_position()
        for node in self.map.network.nodes:
            if isinstance(node, nodes.SimpleSwitch):
                if (
                    np.linalg.norm(
                        self.screen_coordinates(node.coordinates) - mouse_position
                    )
                    < 10
                ):
                    node.switch()
