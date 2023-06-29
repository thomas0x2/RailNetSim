import numpy as np


class Node:
    """
    A Node is an end point for a Track

    Attributes:
        id (str): The ID of the Node, usually the coordinates seperated by a "-"
        coordinates (np.array): The coordinates where the node lies
        tracks (List): The tracks that are connected to this node (max 3)
        adj_nodes (List): The nodes that are adjacent to this node (max 3)
    """

    def __init__(self, id: str, coordinates: tuple):
        self.id = id
        self.coordinates = np.array(coordinates)
        self.tracks = []
        self.adj_nodes = []

    def getDirectionToNode(self, node) -> np.ndarray:
        """
        Get the normalized direction vector to another node

        Args:
            node (Node): The node to which the direction vector points

        Returns:
            np.ndarray: A two dimensional normalized vector pointing towards node
        """
        direction = node.getCoordinates() - self.coordinates
        norm_direction = direction / np.linalg.norm(direction)
        return norm_direction

    def getDistanceToNode(self, node) -> float:
        translated_vector = node.coordinates - self.coordinates
        return np.linalg.norm(translated_vector)

    def addAdjNode(self, node):
        self.adj_nodes.append(node)

    def addTrack(self, track):
        self.tracks.append(track)

    def connectNodes(node1, node2):
        node1.addAdjNode(node2)
        node2.addAdjNode(node1)

    def getCoordinates(self):
        return self.coordinates

    def getTracks(self):
        return self.tracks

    def getAdjNodes(self):
        return self.adj_nodes

    def getID(self):
        return self.id

    def coordinatesToID(coordinates):
        coordinates_str = []
        for i in range(2):
            if coordinates[i] < 0:
                coordinates_str.append(f"({str(coordinates[i]*(-1)).zfill(4)})")
            else:
                coordinates_str.append(str(coordinates[i]).zfill(4))
        return f"{coordinates_str[0]}-{coordinates_str[1]}"

    def __str__(self):
        return f"NODE: {self.id} ----- COORDINATES: {self.coordinates}"

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if all(self.getCoordinates()[i] == other.getCoordinates()[i] for i in range(2)):
            return True
        else:
            return False
