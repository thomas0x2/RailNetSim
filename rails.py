import numpy as np

"""
TO-DO:
    * Make Nodes from parallel Nodes stretch visually apart so trains traverse the node in parallel lines.
    * Create switches
    * Create end nodes
    * Create Stations
"""


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
        self.id = f"{id}H"
        self.nodes = np.array((from_node, to_node))
        self.max_velocity = max_velocity

    def getNodes(self):
        return self.nodes

    def getID(self):
        return self.id

    def getMaxVelocity(self):
        return self.max_velocity

    def getDirection(self, to_node: Node, from_node: Node = None):
        if from_node is None:
            for node in self.getNodes():
                if to_node != node:
                    from_node = node
        translated_vector = to_node.getCoordinates() - from_node.getCoordinates()
        return translated_vector / self.getTrackModelDistance()

    def getTrackModelDistance(self):
        translated_vector = (
            self.nodes[0].getCoordinates() - self.nodes[1].getCoordinates()
        )
        return np.linalg.norm(translated_vector)

    def isParallel(self, other):
        if not isinstance(other, Track):
            return False
        if all(self.nodes[i] == other.getNodes()[i] for i in range(2)):
            return True
        return False

    def getRampStructure(track, ramp_length: int = 21):
        from_node, to_node = track.getNodes()
        direction = from_node.getDirectionToNode(to_node)
        on_ramp_direction = direction + np.array([-direction[1], direction[0]])
        off_ramp_direction = -direction + np.array([-direction[1], direction[0]])

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

    def createParallelTrack(track, max_velocity: int = 180):
        if not isinstance(track, Track):
            return
        parallel_track_nodes = Track.getRampStructure(track)
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
        new_track = Track(
            f"{track.getID()}",
            parallel_track_nodes[1],
            parallel_track_nodes[2],
            max_velocity,
        )

        return list([new_track, ramp_on, ramp_off])

    def __str__(self):
        return f"TRACK: {self.id} ----- COORDINATES: {self.getNodes()[0].getCoordinates()} to {self.getNodes()[1].getCoordinates()}"
