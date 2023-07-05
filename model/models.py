import pygame
from model.nodes import Node
from model.nodes import SimpleSwitch
from model.tracks import Track
from model.trains import Train
import controller.controls as controls
import numpy as np
import math

DEFAULT_TRAIN_COLOR = pygame.Color(204, 0, 0)
DEFAULT_TRACK_DARK = pygame.Color(255, 255, 255)
DEFAULT_TRACK_LIGHT = pygame.Color(25, 50, 77)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0, 0, 255)


class Model:
    """
    A Model is a visual representation of a class from the simulation.
    """

    def __init__(self, color: pygame.Color, position: list = [0, 0]):
        self.color = color
        self.position = position

    def draw(self, surface: pygame.Surface):
        pass


class TrackModel(Model):
    """
    A TrackModel is a visual representation of a Track from the simulation.

    Attributes:
        track (Track): The track that is represented
        color (pygame.Color): The color of the track
        thickness (int): The thickness of the track
    """

    def __init__(
        self,
        track: Track,
        color: pygame.Color = DEFAULT_TRACK_LIGHT,
        thickness: int = 3,
    ):
        position = track.nodes[0].coordinates + track.nodes[1].coordinates[0] // 2
        super().__init__(color, position)
        self.track = track
        self.thickness = thickness

    def getVisualThickness(self, zoom: float) -> int:
        """
        Returns the thickness of the track in pixels, depending on the zoom level.

        Args:
            zoom (float): The current zoom level of the view

        Returns:
            int: The thickness of the track in pixels
        """
        return max(int(self.thickness * zoom), 1)

    def draw(self, surface: pygame.Surface, view, aa_mode: bool = True):
        """
        Draws the track on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on
            view (MapView): The view that determines the currently shown area
            aa_mode (bool, optional): Determines if anti-aliasing is used
        """
        relative_start = view.screen_coordinates(self.track.nodes[0].coordinates)
        relative_end = view.screen_coordinates(self.track.nodes[1].coordinates)
        if aa_mode:
            pygame.draw.aaline(surface, self.color, relative_start, relative_end)
        else:
            pygame.draw.line(
                surface,
                self.color,
                relative_start,
                relative_end,
                self.getVisualThickness(view.zoom),
            )


class TrainModel(Model):
    """
    A TrainModel is a visual representation of a Train from the simulation.

    Attributes:
        train (Train): The train that is represented
        color (pygame.Color): The color of the train
        length (int): The length of the train
        width (int): The width of the train
    """

    def __init__(
        self,
        train: Train,
        color: pygame.Color = DEFAULT_TRAIN_COLOR,
        length: int = 55,
        width: int = 11,
    ):
        self.length = length
        self.width = width
        self.train = train
        super().__init__(color, train.position)

    def draw(self, surface: pygame.Surface, view):
        """
        Draws the train on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on
            view (MapView): The view that determines the currently shown area
        """
        center = view.screen_coordinates(self.position)

        direction = self.train.getTrainDirection()

        alpha = math.atan2(direction[1], direction[0])

        # Calculate half of the width and height of the rectangle
        half_width = self.width * view.zoom / 2
        half_length = self.length * view.zoom / 2

        # Calculate the corner coordinates
        corner1 = (
            center[0] - math.cos(alpha) * half_length + math.sin(alpha) * half_width,
            center[1] - math.sin(alpha) * half_length - math.cos(alpha) * half_width,
        )
        corner2 = (
            center[0] - math.cos(alpha) * half_length - math.sin(alpha) * half_width,
            center[1] - math.sin(alpha) * half_length + math.cos(alpha) * half_width,
        )
        corner3 = (
            center[0] + math.cos(alpha) * half_length - math.sin(alpha) * half_width,
            center[1] + math.sin(alpha) * half_length + math.cos(alpha) * half_width,
        )
        corner4 = (
            center[0] + math.cos(alpha) * half_length + math.sin(alpha) * half_width,
            center[1] + math.sin(alpha) * half_length - math.cos(alpha) * half_width,
        )

        pygame.draw.polygon(surface, self.color, (corner1, corner2, corner3, corner4))


class NodeModel(Model):
    """
    A NodeModel is a visual representation of a Node from the simulation.

    Attributes:
        node (Node): The node that is represented
        color (pygame.Color): The color of the node
        radius (int): The radius of the node
    """

    def __init__(
        self,
        node: Node,
        color: pygame.Color = DEFAULT_TRACK_LIGHT,
        radius: int = 7,
    ):
        super().__init__(color, node.coordinates)
        self.node = node
        self.radius = radius

    def draw(self, surface: pygame.Surface, view):
        """
        Draws the node on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on
            view (MapView): The view that determines the currently shown area

        TODO:
            * Make the node transparent when the mouse is over it
        """
        center = view.screen_coordinates(self.position)
        activation_rect = pygame.Rect(
            center[0] - self.radius * 2,
            center[1] - self.radius * 2,
            self.radius * 4,
            self.radius * 4,
        )
        circle_color = self.color
        circle_color.a = 20
        if activation_rect.collidepoint(pygame.mouse.get_pos()):
            circle_color.a = 5
            pygame.draw.circle(surface, circle_color, center, self.radius * view.zoom)
            if isinstance(self.node, SimpleSwitch):
                self.draw_switch_direction(surface, center, view)

        else:
            pygame.draw.circle(
                surface, circle_color, center, int(self.radius * 0.3) * view.zoom
            )

    def draw_switch_direction(self, surface, center, view):
        direction_out = self.node.getDirectionTo(self.node.getNextNodeFromIndex(0))
        direction_in = self.node.getDirectionTo(self.node.adj_nodes[0])
        pygame.draw.lines(
            surface,
            RED,
            False,
            [center, center + direction_out * 10 * view.zoom],
            int(3 * view.zoom),
        )
        triangle_base_length = self.radius * view.zoom
        triangle_height = 0.5 * self.radius * view.zoom

        perpendicular_vector = pygame.Vector2(direction_in[1], -direction_in[0])
        perpendicular_vector.normalize_ip()

        triangle_vertices = [
            center,
            center
            + direction_in * triangle_height
            - perpendicular_vector * (triangle_base_length / 2),
            center
            + direction_in * triangle_height
            + perpendicular_vector * (triangle_base_length / 2),
        ]
        pygame.draw.polygon(surface, BLUE, triangle_vertices)
