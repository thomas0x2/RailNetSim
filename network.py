import numpy as np

from tracks import Track
from nodes import Node
from trains import Train


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
        self.nodes = []
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
                    parallel_tracks = self.createParallelTrack(
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
        max_velocity: int = 50,
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
        new_track = Track(f"{track_id}C", from_node, to_node, max_velocity)

        for track in self.tracks:
            if track.isParallel(new_track):
                new_track = self.createParallelTrack(new_track, max_velocity)

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
        max_velocity: int = 50,
        max_acceleration: int = 1.3,
        number_wagons: int = 0,
        number_cars: int = 1,
    ):
        new_train = Train(
            id,
            home_node,
            max_velocity=max_velocity,
            max_acceleration=max_acceleration,
            number_wagons=number_wagons,
            number_cars=number_cars,
        )
        self.trains.append(new_train)
        return new_train

    def createParallelTrack(self, track, max_velocity: int = 50, step_size=0):
        """
        TODO:
            * Once ramp nodes/switches are sorted out this function should only check the Tracks of track.getNodes()
            * Step_size needs to be implemented
        """
        if not isinstance(track, Track):
            return
        found_free_track = False
        to_right = True
        i = 0

        while not found_free_track:
            if to_right:
                suffix = "R"
            else:
                suffix = "L"

            parallel_track_nodes = Track.getRampStructure(track, to_right=to_right)
            new_track = Track(
                f"{track.getID()}{suffix}",
                parallel_track_nodes[1],
                parallel_track_nodes[2],
                max_velocity,
            )
            ramp_on = Track(
                f"{track.getID()}R",
                parallel_track_nodes[0],
                parallel_track_nodes[1],
                max_velocity,
            )
            ramp_off = Track(
                f"{track.getID()}R",
                parallel_track_nodes[2],
                parallel_track_nodes[3],
                max_velocity,
            )
            if i % 2 == 0 and i > 0:
                step_size += 1
                new_track, ramp_on, ramp_off = self.createParallelTrack(
                    new_track, max_velocity, step_size=step_size
                )
            if any(
                new_track.isParallel(other_track) for other_track in self.getTracks()
            ):
                to_right = not to_right
                print(f"{track.getID()} is parallel")
            else:
                found_free_track = True
            i += 1

        return list([new_track, ramp_on, ramp_off])
