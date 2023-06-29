import pygame
from nodes import Node
from tracks import Track
from trains import Train
from controls import MapView
import numpy as np
import math

DEFAULT_TRAIN_COLOR = pygame.Color(204, 0, 0)
DEFAULT_TRACK_DARK = (255, 255, 255)
DEFAULT_TRACK_LIGHT = (25, 50, 77)


class Model:
    def __init__(self, color: pygame.Color, position: list = [0, 0]):
        self.color = color
        self.position = position

    def draw(self, surface: pygame.Surface):
        pass


class TrackModel(Model):
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

    def getVisualThickness(self, zoom: float):
        return max(int(self.thickness * zoom), 1)

    def draw(self, surface: pygame.Surface, view, aa_mode: bool = True):
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

    def draw(self, surface: pygame.Surface, view: MapView):
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
