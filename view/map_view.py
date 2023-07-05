import pygame
import numpy as np
import model.nodes as nodes

from model.environment import Map


def clamp(value, value_max, value_min):
    return max(min(value, value_max), value_min)


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

    def handle_node_collision(self, window_view, mouse_position, left=True):
        for node in self.map.network.nodes:
            if isinstance(node, nodes.SimpleSwitch):
                if (
                    np.linalg.norm(
                        self.screen_coordinates(node.coordinates) - mouse_position
                    )
                    < 10
                ):
                    if left:
                        window_view.add_window((600, 400), node.id, node)
                    else:
                        node.switch()
