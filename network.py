import pygame
import numpy as np

from rails import Track
from rails import Node
from trains import Train

TRACK_DARK = (255, 255, 255)
TRACK_LIGHT = (25, 50, 77)


class RailNetwork:
    """
    The Collection of all nodes and tracks. Represents a graph.

    Attributes:
        genesis (Node): The initial Node when the Network is created. Coordinates are (0, 0)
        nodes (List): The list of all nodes in the graph
        tracks (List): The list of all tracks in the graph
        ramps (List): The list of all ramps in the graph. Ramps are tracks that connect a track with a switch
    """

    def __init__(self):
        self.genesis = Node("0000-0000", (0, 0))
        self.nodes = [self.genesis]
        self.tracks = []
        self.ramps = []
        self.trains = []

    def getNodes(self):
        return self.nodes

    def getTracks(self):
        return self.tracks

    def getRamps(self):
        return self.ramps

    def addNodeFromCoordinates(self, coordinates: tuple, id=None):
        if id is None:
            id = Node.coordinatesToID(coordinates)
        # Check if node is in network
        new_node = Node(id, coordinates)
        for node in self.getNodes():
            if new_node == node:
                return node
        self.nodes.append(new_node)
        return new_node

    def addNode(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)

    def addTrakk(self, track: Track):
        for node in track.getNodes():
            self.addNode(node)
        if track not in self.getTracks():
            from_node, to_node = track.getNodes()
            for old_track in self.tracks:
                if old_track.isParallel(track):
                    parallel_tracks = Track.createParallelTrack(
                        track, track.getMaxVelocity()
                    )
                    self.tracks.append(parallel_tracks[0])
                    self.addRamp(parallel_tracks[1])
                    self.addRamp(parallel_tracks[2])
                    return
            self.tracks.append(track)
            Node.connectNodes(from_node, to_node)
            from_node.addTrack(track)
            to_node.addTrack(track)

    def addRamp(self, ramp: Track):
        for node in ramp.getNodes():
            self.addNode(node)
        if ramp not in self.ramps:
            self.ramps.append(ramp)

    def addTrack(
        self,
        track_id: str,
        from_node: Node,
        to_node: Node = None,
        to_coordinates: tuple = None,
        max_velocity: int = 180,
    ):
        """
        Adds a Track to the graph. Can be given either a node or coordinates. If both are given the node is used.
        Also checks for parallel rails and adds ramps accordingly.

        Args:
            track_id (str): The ID for the track
            from_node (Node): The node the tracks starts from
            to_coordinates (tuple): The coordinates where the track leads to
            to_node (Node): The node where the track leads to
            max_velocity (int): The maximum velocity a train can drive on the track
        """
        if to_node is None:
            if to_coordinates is None:
                print("Please add either coordinates or a Node to connect the rail to!")
                return
            to_node = self.addNodeFromCoordinates(to_coordinates)
        new_track = Track(track_id, from_node, to_node, max_velocity)

        for track in self.tracks:
            if track.isParallel(new_track):
                new_track = Track.createParallelTrack(new_track, max_velocity)

        if isinstance(new_track, list):
            self.addTrakk(new_track[0])
            self.addRamp(new_track[1])
            self.addRamp(new_track[2])
        else:
            self.addTrakk(new_track)

    def addTrain(
        self,
        id: str,
        home_node: Node,
        max_velocity: int = 180,
        max_acceleration: int = 200,
        number_wagons: int = 0,
        number_cars: int = 1,
    ):
        new_train = Train(
            id,
            home_node,
            max_velocity=max_acceleration,
            max_acceleration=max_acceleration,
            number_wagons=number_wagons,
            number_cars=number_cars,
        )
        self.trains.append(new_train)
        return new_train

    def draw(
        self,
        surface: pygame.Surface,
        map_position: tuple,
        zoom: float,
        dark_theme: bool = False,
    ):
        """
        Draws the tracks on a surface using pygame

        Args:
            surface (pygame.Surface): The surface to draw on
            map_position (tuple): The current position of the map
            zoom (float): The zooming factor
            dark_theme (bool): If the dark theme is supposed to be used. Defaults to False
        """
        if dark_theme:
            track_color = TRACK_DARK
        else:
            track_color = TRACK_LIGHT
        for track in self.tracks:
            start, end = [track.getNodes()[i].getCoordinates() for i in range(2)]
            relative_start = np.array(start) * zoom + np.array(map_position)
            relative_end = np.array(end) * zoom + np.array(map_position)
            pygame.draw.aaline(surface, track_color, relative_start, relative_end)
        for ramp in self.ramps:
            start, end = [ramp.getNodes()[i].getCoordinates() for i in range(2)]
            relative_start = np.array(start) * zoom + np.array(map_position)
            relative_end = np.array(end) * zoom + np.array(map_position)
            pygame.draw.aaline(surface, track_color, relative_start, relative_end)
        for train in self.trains:
            train.draw(surface, map_position, zoom)
