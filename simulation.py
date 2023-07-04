import pygame
import controls
from controls import MapView
from environment import Map
from enum import Enum
import numpy as np
from trains import Train

"""
Utility Methods
"""


def kmh_to_ms(kmh: float):
    return kmh / 3.6


def ms_to_kmh(ms: float):
    return ms * 3.6


"""
Time
"""
clock = pygame.time.Clock()


class GlobalSpeed(Enum):
    """
    Defines the global speed. Slow makes everything run in real-time.
    """

    SLOW = 1
    NORMAL = 5
    QUICK = 10
    FAST = 25


GLOBAL_SPEED = GlobalSpeed.NORMAL
"""
Environment
"""
map = Map([2 * 7680, 2 * 4320])
network = map.getRailNetwork(False)

"""
Rails
"""
node_coordinates = [
    [0, 0],
    [0, 310],
    [0, -40],
    [0, -250],
    [240, -160],
    [0, -510],
    [870, -160],
    [0, 1120],
]
adjacency_matrix = [
    [0, 4, 1, 0, 0, 0, 0, 0],
    [4, 0, 0, 0, 0, 0, 0, 2],
    [1, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 2, 0, 0],
    [0, 0, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0],
]
max_velocities_in_kmh = np.array(
    [100, 100, 80, 60, 80, 180, 200, 200, 200, 160, 320, 200, 160, 160]
)
max_velocities_in_ms = kmh_to_ms(max_velocities_in_kmh)
network.initNodesAndTracks(node_coordinates, adjacency_matrix, max_velocities_in_ms)
for node in network.nodes[0].adj_nodes:
    print(node)

"""
Trains
"""
train1 = Train("766RHZ", network.nodes[0])
network.trains.append(train1)
train1.addRoute([network.nodes[i] for i in [1, 7, 1, 0]])

train2 = Train("K677D8", network.nodes[0])
network.trains.append(train2)
train2.addRoute([network.nodes[i] for i in [2, 4, 6, 4, 3, 5, 3, 2, 0]])
print(train2.getRouteLogs())
for node in network.nodes:
    print(node)

"""
Simulation
"""
pygame.init()
window = pygame.display.set_mode((1280, 720))
view = MapView(map)
pygame.display.set_caption("Traffic Network Simulator")
key_state = {}
running = True

while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key_state[event.key] = True
        elif event.type == pygame.KEYUP:
            key_state[event.key] = False

    controls.handle_view_controls(view, key_state)
    controls.handle_user_input(view)

    # Game logic
    view.clamp()

    # Map
    map.render(window, view)

    # Trains
    fps = clock.get_fps()
    train1.drive(
        fps, target_velocity_in_ms=kmh_to_ms(100), global_speed=GLOBAL_SPEED.value
    )
    train2.drive(
        fps, target_velocity_in_ms=kmh_to_ms(200), global_speed=GLOBAL_SPEED.value
    )

    pygame.display.update()

pygame.quit()
