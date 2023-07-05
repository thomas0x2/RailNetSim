import numpy as np
from enum import Enum
from view.windows import Window
import time


class Node:
    """
    A Node is an Network element that can represent an end point, a platform or a switch.

    Attributes:
        id (str): The ID of the Node, usually the coordinates seperated by a "-"
        coordinates (np.array): The coordinates where the node lies
        tracks (List): The tracks that are connected to this node (max 3)
        adj_nodes (List): The nodes that are adjacent to this node (max 3)
    """

    def __init__(self, id: str, coordinates: tuple, adj_nodes: list = None):
        self.id = id
        self.coordinates = np.array(coordinates)
        self.tracks = []
        self.adj_nodes = []

    def getDirectionTo(self, node) -> np.ndarray:
        """
        Get the normalized direction vector to another node

        Args:
            node (Node): The node to which the direction vector points

        Returns:
            np.ndarray: A two dimensional normalized vector pointing towards node
        """
        direction = node.coordinates - self.coordinates
        norm_direction = direction / np.linalg.norm(direction)
        return norm_direction

    def getDistanceToNode(self, node) -> float:
        """
        Get the distance to another node

        Args:
            node (Node): The node to which the distance is calculated

        Returns:
            float: The distance to the other node"""
        translated_vector = node.coordinates - self.coordinates
        return np.linalg.norm(translated_vector)

    def connectNodes(self, other_node):
        """
        Connects two nodes by adding the other node to the adj_nodes list of both nodes

        Args:
            other_node (Node): The node to which this node is connected
        """
        self.adj_nodes.append(other_node)
        other_node.adj_nodes.append(self)

    def coordinatesToID(coordinates: tuple) -> str:
        """
        Converts coordinates to an ID

        Args:
            coordinates (tuple): The coordinates to be converted

        Returns:
            str: The ID of the coordinates"""
        coordinates_str = []
        for i in range(2):
            if coordinates[i] < 0:
                coordinates_str.append(f"({str(coordinates[i]*(-1)).zfill(4)})")
            else:
                coordinates_str.append(str(coordinates[i]).zfill(4))
        return f"{coordinates_str[0]}-{coordinates_str[1]}"

    def getNextNodeFromIndex(self, next_node_index: int):
        return self.adj_nodes[next_node_index]

    def getTrackTo(self, node):
        for track in self.tracks:
            if node in track.nodes:
                return track

    def getIndex(self, node):
        return self.adj_nodes.index(node)

    def __str__(self):
        return f"{self.id}              Cords. {self.coordinates}"

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if all(self.coordinates[i] == other.coordinates[i] for i in range(2)):
            return True
        else:
            return False


class SimpleSwitch(Node):
    def __init__(self, id: str, coordinates: tuple, adj_nodes: list = None):
        super().__init__(id, coordinates, adj_nodes)
        self.switch_state = 0

    def switch(self):
        self.switch_state = (self.switch_state + 1) % (len(self.adj_nodes) - 1)

    def getDelay(self, global_speed: int):
        return self.delay / global_speed

    def getNextNodeFromIndex(self, previous_node_index: int):
        if self.switch_state == 0:
            if 0 <= previous_node_index <= 1:
                return self.adj_nodes[1 - previous_node_index]
        if self.switch_state == 1:
            if previous_node_index == 0 or previous_node_index == 2:
                return self.adj_nodes[2 - previous_node_index]
        if self.switch_state == 2:
            if previous_node_index == 0 or previous_node_index == 3:
                return self.adj_nodes[3 - previous_node_index]
        return None

    def getNextNodeFrom(self, previous_node: Node):
        previous_node_index = self.getIndex(previous_node)
        return self.getNextNodeFromIndex(previous_node_index)

    def getTrackFrom(self, previous_node: Node):
        previous_node_index = self.getIndex(previous_node)
        if self.switch_state == 0:
            if 0 <= previous_node_index <= 1:
                return self.tracks[1 - previous_node_index]
        if self.switch_state == 1:
            if previous_node_index == 0 or previous_node_index == 2:
                return self.tracks[2 - previous_node_index]
        if self.switch_state == 2:
            if previous_node_index == 0 or previous_node_index == 3:
                return self.tracks[3 - previous_node_index]
        return None


# Make Switches a collection of nodes
class ComplexSwitch:
    pass
