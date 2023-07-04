import numpy as np

from tracks import Track
from nodes import Node
from nodes import SimpleSwitch
from trains import Train
from typing import Union


class RailNetwork:
    """
    The Collection of all nodes and tracks. Represents a graph.

    Attributes:
        nodes (List): The list of all nodes in the graph
        tracks (List): The list of all tracks in the graph
        ramps (List): The list of all ramps in the graph. Ramps are tracks that connect nodes inside a switch
        trains (List): The list of all trains in the graph
    """

    def __init__(self):
        self.nodes = []
        self.tracks = []
        self.ramps = []
        self.trains = []
        self.adjacency_matrix = None

    def addNode(self, node: Node):
        """
        If the node isn't already inside the nodes list, it is added.

        Args:
            node (Node): Node to add to the network
        """
        if node not in self.nodes:
            self.nodes.append(node)

    def addNodes(self, node_coordinates: list):
        """
        Adds nodes from a vector of coords.

        Args:
            node_coordinates (List): Vector of coords.
        """
        for coordinate in node_coordinates:
            new_node = Node(
                f"N.{len(self.nodes)}:{Node.coordinatesToID(coordinate)}", coordinate
            )
            self.nodes.append(new_node)

    def addTrack(self, track):
        """
        Adds a Track to the network. Can also add a list of tracks.

        Args:
            track : Track of List of Tracks that are added
        """
        if isinstance(track, list):
            if track[1] not in self.tracks:
                for i in range(len(track)):
                    node_0, node_1 = track[i].nodes
                    node_0.connectNodes(node_1)
                    node_0.tracks.append(track[i])
                    node_1.tracks.append(track[i])
                    if i == 0:
                        self.tracks.append(track[i])
                    else:
                        self.ramps.append(track[i])

        elif isinstance(track, Track):
            if track not in self.tracks:
                node_0, node_1 = track.nodes
                node_0.connectNodes(node_1)
                node_0.tracks.append(track)
                node_1.tracks.append(track)
                self.tracks.append(track)

    def createTrackFromNodes(
        self,
        track_id: str,
        node_0: Node,
        node_1: Node,
        max_velocity: int = 50,
    ) -> Union[Track, list]:
        """
        Creates a Track from Nodes and returns it. If the track is parallel to an existing track in the network,
        a parallel Track is created and a list of the track and its ramps is created.

        Args:
            track_id (str): The ID for the track
            node_0 (Node): The first node of the track
            node_1 (Node): The second node of the track
            max_velocity (int): The maximum velocity a train can drive on the track

        Returns:
            (Union[Track, list]): A list if the track is parallel to another track otherwise a Track.)
        """
        new_track = Track(f"{track_id}C", node_0, node_1, max_velocity)

        for track in self.tracks:
            if track.isParallel(new_track):
                new_track = self.createParallelTrack(new_track, max_velocity)

        return new_track

    def addTracksFromMatrix(
        self, adjacency_matrix: np.ndarray, max_velocities_in_ms: np.ndarray = None
    ):
        """
        Adds Tracks to the network from an adjacency matrix. The adjacency matrix is a matrix that represents the
        connections between nodes. The matrix is symmetric and the value of the matrix represents the number of tracks
        between the nodes. If the value is 0, there is no track between the nodes. If the value is i, there are i tracks
        between the nodes.

        Args:
            adjacency_matrix (np.ndarray): The adjacency matrix of the network
            max_velocities_in_ms (np.ndarray, optional): The max velocities of the tracks in m/s
        """
        track_number = 0
        self.adjacency_matrix = adjacency_matrix
        for i in range(len(adjacency_matrix)):
            for j in range(i):
                if adjacency_matrix[i][j] > 0:
                    for k in range(adjacency_matrix[i][j]):
                        max_velocity = 50
                        if max_velocities_in_ms[track_number] is not None:
                            max_velocity = max_velocities_in_ms[track_number]
                        self.addTrack(
                            self.createTrackFromNodes(
                                f"Track No. {track_number}",
                                self.nodes[i],
                                self.nodes[j],
                                max_velocity=max_velocity,
                            )
                        )
                        track_number += 1

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
                f"{track.id}{suffix}",
                parallel_track_nodes[1],
                parallel_track_nodes[2],
                max_velocity,
            )
            ramp_on = Track(
                f"{track.id}R",
                parallel_track_nodes[0],
                parallel_track_nodes[1],
                max_velocity,
            )
            ramp_off = Track(
                f"{track.id}R",
                parallel_track_nodes[2],
                parallel_track_nodes[3],
                max_velocity,
            )
            if i % 2 == 0 and i > 0:
                step_size += 1
                new_track, ramp_on, ramp_off = self.createParallelTrack(
                    new_track, max_velocity, step_size=step_size
                )
            if any(new_track.isParallel(other_track) for other_track in self.tracks):
                to_right = not to_right
            else:
                found_free_track = True
            i += 1
        return list([new_track, ramp_on, ramp_off])

    def initNodesAndTracks(
        self,
        node_coordinates: list,
        adjacency_matrix: np.ndarray,
        max_velocities_in_ms: np.ndarray = None,
    ):
        """
        Creates Nodes and Tracks from coordinates and an adjacency matrix.

        Args:
            node_coordinates (list): A list of coordinates for the nodes
            adjacency_matrix (np.ndarray): The adjacency matrix of the network
        """
        for i, coordinates in enumerate(node_coordinates):
            if (
                3
                <= sum(adjacency_matrix[i][j] for j in range(len(adjacency_matrix[i])))
                <= 4
            ):
                new_node = SimpleSwitch(
                    f"SS.{i}:{Node.coordinatesToID(coordinates)}", coordinates
                )
            else:
                new_node = Node(
                    f"N.{i}:{Node.coordinatesToID(coordinates)}", coordinates
                )
            self.addNode(new_node)

        self.addTracksFromMatrix(
            adjacency_matrix, max_velocities_in_ms=max_velocities_in_ms
        )
