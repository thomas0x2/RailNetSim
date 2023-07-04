from enum import Enum
import pygame
from network import RailNetwork
from models import TrainModel
from models import TrackModel
from models import NodeModel
from nodes import Node

BACKGROUND_LIGHT = (242, 242, 242)
BACKGROUND_DARK = (70, 70, 70)


class Map:
    """
    The Map determines the size of the viewable area, holds the Network and other environmental objects, and supplies the View

    Attributes:
        size (list): The width and length of the viewable area
        network (RailNetwork): The network that runs on the map
        view (MapView): The view element that determines the currently shown area.
    """

    def __init__(self, size: list):
        self.size = size
        self.network = None

    def getRailNetwork(self, drawer_mode: bool = False) -> RailNetwork:
        """
        Creates and returns the singleton Rail Network. If drawer_mode is applied it also adds a central node.

        Args:
            drawer_mode(bool, optional): Determines if drawer_mode is used.
        """
        if self.network is None:
            self.network = RailNetwork()
            if drawer_mode:
                self.network.nodes.append(Node("0:0000-0000", (0, 0)))
        return self.network

    def render(
        self,
        surface: pygame.Surface,
        view,
        dark_theme: bool = False,
        aa_mode: bool = True,
    ):
        """
        Draws the tracks on a surface using pygame

        Args:
            surface (pygame.Surface): The surface to draw on
        """
        surface.fill(BACKGROUND_LIGHT)
        for track in self.getRailNetwork().tracks:
            TrackModel(track).draw(surface, view)
        for ramp in self.getRailNetwork().ramps:
            TrackModel(ramp).draw(surface, view)
        for node in self.getRailNetwork().nodes:
            NodeModel(node).draw(surface, view)
        for train in self.getRailNetwork().trains:
            TrainModel(train).draw(surface, view)
