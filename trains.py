import pygame
from rails import Node
from rails import Track
import numpy as np
import math
from collections import deque
from clock import GLOBAL_TIME

TRAIN_LENGTH = 55
TRAIN_WIDTH = 11
TRAIN_COLOR = pygame.Color(204, 0, 0)
VELOCITY_FACTOR = GLOBAL_TIME.value * 0.02


class Train:
    def __init__(
        self,
        id: str,
        home_node: Node,
        max_velocity: int = 180,
        max_acceleration=200,
        number_wagons: int = 0,
        number_cars: int = 1,
    ):
        self.id = id
        self.home_node = home_node
        self.route = deque()
        self.route.append(home_node)
        self.has_arrived = True
        self.track = None
        self.s_track = 0

        self.number_wagons = number_wagons
        self.number_cars = number_cars
        self.color = TRAIN_COLOR

        self.position = home_node.getCoordinates()
        self.direction = [1, 0]
        self.max_velocity = max_velocity
        self.velocity = 0
        self.target_velocity = 0
        self.max_acceleration = max_acceleration

    def setTargetVelocity(self, target_velocity: int):
        if target_velocity is None:
            return
        if target_velocity < 0:
            target_velocity = 0
        target_velocity = min(target_velocity, self.max_velocity)
        if not self.track is None:
            target_velocity = min(target_velocity, self.track.getMaxVelocity())
        self.target_velocity = target_velocity

    def getRoute(self) -> deque:
        return self.route

    def getTrack(self) -> Track:
        return self.track

    def getRouteLogs(self) -> str:
        string = f"{self.id} ROUTE # "
        for node in self.route:
            string += f"{node.getID()} VIA "
        return string

    def addNodeToRoute(self, node: Node):
        if node in self.route[-1].getAdjNodes():
            self.route.append(node)
            self.has_arrived = False
        if self.track is None:
            self.track = self.getNextTrack()

    def setHasArrived(self):
        if len(self.route) < 2:
            self.has_arrived = True
            return True
        else:
            self.has_arrived = False
            return False

    def getHasArrived(self):
        return self.has_arrived

    def getNextTrack(self) -> bool:
        if self.setHasArrived():
            return
        for track in self.route[0].getTracks():
            if self.route[1] in track.getNodes():
                return track
        return

    def getTrainPosition(self):
        return self.position

    def accelerate(self, acceleration=None):
        if acceleration is None:
            acceleration = self.max_acceleration
        new_velocity = min(
            self.velocity + acceleration, self.max_velocity, self.target_velocity
        )
        if self.track is not None:
            new_velocity = min(new_velocity, self.track.getMaxVelocity())
        self.velocity = new_velocity

    def decelerate(self, deceleration=None):
        if deceleration is None:
            deceleration = self.max_acceleration
        self.velocity = max(self.velocity - deceleration, 0)

    def drive(self, target_velocity=None):
        if self.setHasArrived():
            return
        self.setTargetVelocity(target_velocity)
        if self.velocity < self.target_velocity:
            self.accelerate()
        if self.velocity > self.target_velocity:
            self.decelerate()

        self.direction = self.track.getDirection(self.route[1])
        delta_s = self.velocity * VELOCITY_FACTOR
        self.s_track += delta_s
        if self.s_track >= self.track.getTrackModelDistance():
            self.route.popleft()
            self.track = self.getNextTrack()
            self.position = self.route[0].getCoordinates()
            self.s_track = 0
        else:
            self.position = self.position + self.direction * delta_s

    def draw(self, surface, map_position, zoom):
        center_x = self.position[0] * zoom + map_position[0]
        center_y = self.position[1] * zoom + map_position[1]

        if self.has_arrived:
            direction = self.direction
        else:
            direction = self.route[0].getDirectionToNode(self.route[1])

        alpha = math.atan2(direction[1], direction[0])

        # Calculate half of the width and height of the rectangle
        half_width = TRAIN_WIDTH * zoom / 2
        half_length = TRAIN_LENGTH * zoom / 2

        # Calculate the corner coordinates
        corner1 = (
            center_x - half_length * math.cos(alpha) + half_width * math.sin(alpha),
            center_y - half_length * math.sin(alpha) - half_width * math.cos(alpha),
        )
        corner2 = (
            center_x + half_length * math.cos(alpha) + half_width * math.sin(alpha),
            center_y + half_length * math.sin(alpha) - half_width * math.cos(alpha),
        )
        corner3 = (
            center_x - half_length * math.cos(alpha) - half_width * math.sin(alpha),
            center_y - half_length * math.sin(alpha) + half_width * math.cos(alpha),
        )
        corner4 = (
            center_x + half_length * math.cos(alpha) - half_width * math.sin(alpha),
            center_y + half_length * math.sin(alpha) + half_width * math.cos(alpha),
        )

        pygame.draw.polygon(surface, self.color, (corner1, corner3, corner4, corner2))

    """

    def accelerate(self, target_velocity):
        self.current_velocity = min(
            target_velocity,
            self.current_velocity + self.max_acceleration,
            self.current_rail.getMaxSpeed(),
        )

    def drive(self, target_velocity, orientation: Orientation):
        target_velocity = min(self.max_velocity, target_velocity)
        if self.current_velocity < target_velocity:
            self.accelerate(target_velocity)

        direction = self.current_rail.getDirection()
        new_position = (
            self.position
            + orientation.value * direction * self.current_velocity * VELOCITY_FACTOR
        )

        threshold = 0.64
        if orientation.value < 0:
            if (
                np.linalg.norm(new_position - self.current_rail.getStartPoint())
                < threshold
            ):
                link = self.current_rail.getStartLink()
                if link is not None:
                    self.rail = link.getNextRail(False)
                    self.position = self.current_rail.getStartPoint()
                else:
                    return
        if orientation.value > 0:
            if (
                np.linalg.norm(new_position - self.current_rail.getEndPoint())
                < threshold
            ):
                link = self.current_rail.getEndLink()
                if link is not None:
                    self.rail = link.getNextRail(True)
                    self.position = self.current_rail.getEndPoint()
                else:
                    return
        self.position = new_position

    def draw(self, surface, map_x, map_y, zoom):
        center_x = self.position[0] * zoom + map_x
        center_y = self.position[1] * zoom + map_y
        direction = self.current_rail.getDirection()
        alpha = math.atan2(direction[1], direction[0])

        # Calculate half of the width and height of the rectangle
        half_width = TRAIN_WIDTH * zoom / 2
        half_length = TRAIN_LENGTH * zoom / 2

        # Calculate the corner coordinates
        corner1 = (
            center_x - half_length * math.cos(alpha) + half_width * math.sin(alpha),
            center_y - half_length * math.sin(alpha) - half_width * math.cos(alpha),
        )
        corner2 = (
            center_x + half_length * math.cos(alpha) + half_width * math.sin(alpha),
            center_y + half_length * math.sin(alpha) - half_width * math.cos(alpha),
        )
        corner3 = (
            center_x - half_length * math.cos(alpha) - half_width * math.sin(alpha),
            center_y - half_length * math.sin(alpha) + half_width * math.cos(alpha),
        )
        corner4 = (
            center_x + half_length * math.cos(alpha) - half_width * math.sin(alpha),
            center_y + half_length * math.sin(alpha) + half_width * math.cos(alpha),
        )
        pygame.draw.polygon(surface, self.color, (corner1, corner3, corner4, corner2))

    def getTrainPos(self):
        return self.position

    def getTrainSpeed(self):
        return self.current_velocity
"""


class LongDistanceTrain(Train):
    pass


class RegionalTrain(Train):
    pass


class CargoTrain(Train):
    pass
