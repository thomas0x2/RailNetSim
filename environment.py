from enum import Enum
import pygame
from network import RailNetwork
from models import TrainModel
from models import TrackModel
from nodes import Node
from controls import MapView


class Map:
    def __init__(self, size: list):
        self.size = size
        self.network = None
        self.view = None

    def getView(self):
        if self.view is None:
            self.view = MapView(self.size)
        return self.view

    def getRailNetwork(self, drawer_mode=False) -> RailNetwork:
        if self.network is None:
            self.network = RailNetwork()
            if drawer_mode:
                self.network.nodes.append(Node("0000-0000", (0, 0)))
        return self.network

    def render(
        self,
        surface: pygame.Surface,
        dark_theme: bool = False,
        aa_mode: bool = True,
    ):
        """
        Draws the tracks on a surface using pygame

        Args:
            surface (pygame.Surface): The surface to draw on
        """
        for track in self.getRailNetwork().tracks:
            TrackModel(track).draw(surface, self.view)
        for ramp in self.getRailNetwork().ramps:
            TrackModel(ramp).draw(surface, self.view)
        for train in self.getRailNetwork().trains:
            TrainModel(train).draw(surface, self.view)
