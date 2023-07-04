import numpy as np
import pygame

from nodes import Node
from nodes import SimpleSwitch
from tracks import Track
from collections import deque

clock = pygame.time.Clock()


class Train:
    """
    The Class Train represents the trains that ride on the network

    Attributes:
        id (str): Used to identify a train
        home_node (Node): Node where the trains starts and will return to
        route (Deque): A deque that holds the route the train is currently on
        number_cars (int): The number of cars in the train
        number_waggons (int): The number of waggons in the train
        color (pygame.Color): Color of the train
        position (np.ndarray): Coordinates of the current position of the train
        max_velocity (int): Maximum velocity the train can ride in meters per second
        velocity (int): The current velocity of the train in meter per second
        max_acceleration (int): Maximum acceleration the train can achieve in meters per second squared

    """

    def __init__(
        self,
        id: str,
        home_node: Node,
        max_velocity: int = 180,
        max_acceleration: float = 1.3,
        number_wagons: int = 0,
        number_cars: int = 1,
    ):
        self.id = id
        self.home_node = home_node
        self.track = None
        self.route = deque()
        self.route.append(home_node)
        self.previous_node = home_node

        self.number_wagons = number_wagons
        self.number_cars = number_cars

        self.position = home_node.coordinates
        self.max_velocity = max_velocity
        self.velocity = 0
        self.max_acceleration = max_acceleration

    def getTrack(self, previous_node, current_node) -> Track:
        """
        Returns the track the train is currently on

        Returns:
            Track: The track the train is currently on
        """
        if len(self.route) > 1:
            return current_node.getTrack(previous_node, next_node=self.route[1])
        return None

    def getTrainDirection(self) -> np.ndarray:
        """
        Returns the Direction of the train

        returns:
            np.ndarray: Direction of the train
        """
        if len(self.route) > 1:
            return self.route[0].getDirectionTo(self.route[1])
        else:
            return self.route[0].getDirectionTo(self.route[0].adj_nodes[0])

    def getTargetVelocity(self, target_velocity: int) -> int:
        """
        Takes the target velocity. The target velocity is reduces if its too high or increased if its too low.

        Args:
            target_velocity (int): The target_velocity the user wishes to set

        Returns:
            int: The feasible target velocity
        """
        if self.track is None:
            return 0
        if target_velocity is None:
            return
        if target_velocity < 0:
            target_velocity = 0
        target_velocity = min(
            target_velocity, self.max_velocity, self.track.max_velocity
        )
        return target_velocity

    def getRouteLogs(self) -> str:
        string = f"{self.id} Route # "
        for node in self.route:
            string += f"{node.id} VIA "
        return string

    def addRoute(self, nodes: list):
        """
        Adds a list of nodes to the trains route

        Args:
            nodes (list): List of nodes to add to the route
        """
        for node in nodes:
            self.addNodeToRoute(node)

    def addNodeToRoute(self, node: Node):
        """
        Adds a node to the trains route if it is adjacent to the last node in the route

        Args:
            node (Node): The node to add
        """
        if node in self.route[-1].adj_nodes:
            self.route.append(node)
            self.has_arrived = False
            if len(self.route) == 2:
                self.track = self.route[0].getTrackTo(self.route[1])

    def getHasArrived(self) -> bool:
        """
        Checks if the train has a next destination in its route

        Returns:
            bool: True if there is a another destination in its route, False if there is not
        """
        if len(self.route) < 2:
            return True
        else:
            return False

    def accelerate(
        self,
        target_velocity: int,
        acceleration: float = None,
        speed_coefficient: float = 1.0,
    ):
        """
        Accelerates (i.e. increases self.velocity) the train if possible. Acceleration
        will always be higher or equal to 0 and lower or equal to self.max_acceleration

        Args:
            target_velocity (int): The maximum velocity the train is supposed to reach
            acceleration (float, optional): Sets how fast the train should accelerate. Defaults to self.max_acceleration
            speed_coefficient (float, optional): A coefficient that can be used to slow down the acceleration. Defaults to 1.0
        """
        if acceleration is None:
            acceleration = self.max_acceleration
        acceleration = max(min(acceleration, self.max_acceleration), 0)
        new_velocity = min(
            self.velocity + acceleration * speed_coefficient,
            self.max_velocity,
            target_velocity,
        )
        if self.track is not None:
            new_velocity = min(new_velocity, self.track.max_velocity)
        self.velocity = new_velocity

    def decelerate(self, deceleration: float = None, speed_coefficient: float = 1.0):
        """
        Decelerates (i.e. decreases self.velocity) the train. Deceleration will always
        be higher or equal to 0 and lower or equal to self.max_acceleration

        Args:
            deceleration (float, optional): How fast the train should decelerate. Defaults to self.max_acceleration
            speed_coefficient (float, optional): A coefficient that can be used to slow down the deceleration. Defaults to 1.0
        """
        if deceleration is None:
            deceleration = self.max_acceleration
        deceleration = min(max(deceleration, 0), self.max_acceleration)
        self.velocity = max(self.velocity - deceleration * speed_coefficient, 0)

    def drive(self, fps: int, target_velocity_in_ms: int = 100, global_speed: int = 1):
        """
        If the train has a Destination and a Track, this method will accelerate() or decelerate() the train. Until it reached its
        next Destination Node, it will move in the direction of getTrainDirection() according to its current velocity.

        Args:
            fps (int): The current fps of the simulation
            target_velocity (int, optional): The target velocity the train should reach. Defaults to 100.
            global_speed (int, optional): A coefficient that can be used to slow down the train. Defaults to 1.
        """
        if fps == 0 or self.getHasArrived():
            return

        target_velocity = self.getTargetVelocity(target_velocity_in_ms)
        if self.velocity < target_velocity:
            self.accelerate(target_velocity, speed_coefficient=global_speed / fps)
        elif self.velocity > target_velocity:
            self.decelerate(target_velocity, speed_coefficient=global_speed / fps)

        delta_s = self.velocity * global_speed / fps

        if self.reachedNode(delta_s, self.route[1]):
            self.handleNodeReached()
        else:
            self.moveTrain(delta_s)

    def getDistanceFromNode(self, node: Node) -> float:
        """
        Returns the distance of the train to a Node.

        Args:
            node (Node): Node the distance to is to be determined

        Returns:
            float: Distance between train position and Node.
        """
        return np.linalg.norm(self.position - [node.coordinates])

    def reachedNode(self, epsilon: float = 1.0, node: Node = None) -> bool:
        """
        Checks if a train reached its Destination node

        Args:
            epsilon(float, optional): Margin how far the train is allowed to be away from the nexct Node to still consider it reached. Defaults to 1.0

        Returns:
            bool: True if the train reached its next destination
        """
        if node is None:
            node = self.route[1]
        if self.getDistanceFromNode(node) < epsilon:
            return True
        return False

    def handleNodeReached(self):
        self.previous_node = self.route.popleft()
        current_node = self.route[0]
        self.position = current_node.coordinates

        if self.getHasArrived():
            return

        next_node = self.route[1]
        if isinstance(current_node, SimpleSwitch):
            if current_node.getNextNode(self.previous_node) != next_node:
                self.track = None
                self.velocity = 0
                return

        self.track = next_node.getTrackTo(self.route[1])

    def moveTrain(self, delta_s: float):
        self.position = self.position + self.getTrainDirection() * delta_s


class LongDistanceTrain(Train):
    pass


class RegionalTrain(Train):
    pass


class CargoTrain(Train):
    pass
