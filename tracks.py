import numpy as np
from nodes import Node

"""
TO-DO:
    * Make Nodes from parallel Nodes stretch visually apart so trains traverse the node in parallel lines.
    * Create switches
    * Create end nodes
    * Create Stations
"""


class Track:
    """
    A Track is a line where trains can ride on

    Attributes:
        id (str): The ID of the Track
        nodes (np.ndarray): The two nodes that the track connects
        max_velocity (int): The maximum velocity in km/h that a train can drive on this track. 180 km/h if kept empty.
    """

    def __init__(self, id: str, from_node: Node, to_node: Node, max_velocity=180):
        self.id = id
        self.nodes = np.array((from_node, to_node))
        self.max_velocity = max_velocity

    def getDirection(self, to_node: Node, from_node: Node = None) -> np.ndarray:
        """
        Returns the direction of the track as a unit vector

        Args:
            to_node (Node): The node to which the direction is calculated
            from_node (Node, optional): The node from which the direction is calculated. If not given, the other node is looked up and used.

        Returns:
            (np.ndarray): The direction of the track as a unit vector
        """
        if from_node is None:
            for node in self.nodes:
                if to_node != node:
                    from_node = node
        translated_vector = to_node.coordinates - from_node.coordinates
        return translated_vector / np.linalg.norm(translated_vector)

    def isParallel(self, other):
        """
        Checks if the track is parallel to another track

        Args:
            other (Track): The other track to which the track is compared

        Returns:
            (bool): True if the tracks are parallel, False otherwise
        """
        if not isinstance(other, Track):
            return False
        if all(self.nodes[i] == other.nodes[i] for i in range(2)):
            return True
        return False

    def getRampStructure(track, ramp_length: int = 21, to_right=True):
        """
        Creates a ramp structure for a track. The ramp structure consists of two ramp nodes and a track between them.
        The ramp nodes are connected to the track and the track is connected to the nodes of the original track.

        Args:
            track (Track): The track for which the ramp structure is created
            ramp_length (int, optional): The length of the ramp in meters. Defaults to 21.
            to_right (bool, optional): If True, the ramp is created to the right of the track, if False, the ramp is created to the left of the track. Defaults to True.
        """
        from_node, to_node = track.nodes
        direction = from_node.getDirectionTo(to_node)

        if to_right:
            perp_vector = [-direction[1], direction[0]]
        else:
            perp_vector = [direction[1], -direction[0]]

        on_ramp_direction = direction + perp_vector
        off_ramp_direction = -direction + perp_vector

        on_ramp_coordinates = from_node.coordinates + on_ramp_direction * ramp_length
        off_ramp_coordinates = to_node.coordinates + off_ramp_direction * ramp_length

        on_ramp_node = Node(
            f"RAMP{on_ramp_coordinates[0]} {on_ramp_coordinates[1]}",
            on_ramp_coordinates,
        )
        off_ramp_node = Node(
            f"RAMP{off_ramp_coordinates[0]} {off_ramp_coordinates[1]}",
            off_ramp_coordinates,
        )

        return from_node, on_ramp_node, off_ramp_node, to_node

    def __str__(self):
        return f"{self.id}          Coords. {self.nodes[0].coordinates} to {self.nodes[1].coordinates}"
