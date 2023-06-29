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
        from_node (Node): The starting node
        to_node (Node): The end node
        max_velocity (int): The maximum velocity in km/h that a train can drive on this track. 180 km/h if kept empty.
    """

    def __init__(self, id: str, from_node: Node, to_node: Node, max_velocity=180):
        self.id = id
        self.nodes = np.array((from_node, to_node))
        self.max_velocity = max_velocity

    def getNodes(self):
        return self.nodes

    def getID(self):
        return self.id

    def getMaxVelocity(self):
        return self.max_velocity

    def getDirection(self, to_node: Node, from_node: Node = None) -> np.ndarray:
        if from_node is None:
            for node in self.getNodes():
                if to_node != node:
                    from_node = node
        translated_vector = to_node.getCoordinates() - from_node.getCoordinates()
        return translated_vector / self.getTrackModelDistance()

    def getTrackModelDistance(self):
        return self.nodes[0].getDistanceToNode(self.nodes[1])

    def isParallel(self, other):
        if not isinstance(other, Track):
            return False
        if all(self.nodes[i] == other.getNodes()[i] for i in range(2)):
            return True
        return False

    def getRampStructure(track, ramp_length: int = 21, to_right=True):
        from_node, to_node = track.getNodes()
        direction = from_node.getDirectionToNode(to_node)

        if to_right:
            perp_vector = [-direction[1], direction[0]]
        else:
            perp_vector = [direction[1], -direction[0]]

        on_ramp_direction = direction + perp_vector
        off_ramp_direction = -direction + perp_vector

        on_ramp_coordinates = (
            from_node.getCoordinates() + on_ramp_direction * ramp_length
        )
        off_ramp_coordinates = (
            to_node.getCoordinates() + off_ramp_direction * ramp_length
        )

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
        return f"TRACK: {self.id} ----- COORDINATES: {self.getNodes()[0].getCoordinates()} to {self.getNodes()[1].getCoordinates()}"
