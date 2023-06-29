import pygame
import controls
from environment import Map
from enum import Enum
import time

"""
Utility Methods
"""
BACKGROUND_LIGHT = (242, 242, 242)
BACKGROUND_DARK = (70, 70, 70)
DARK_THEME = False


def kmh_to_ms(kmh: float):
    return kmh / 3.6


def ms_to_kmh(ms: float):
    return ms * 3.6


"""
Time
"""
clock = pygame.time.Clock()


class GlobalSpeed(Enum):
    SLOW = 1
    NORMAL = 5
    QUICK = 10
    FAST = 25


GLOBAL_SPEED = GlobalSpeed.NORMAL
"""
Environment
"""
map = Map([2 * 7680, 2 * 4320])
network = map.getRailNetwork(True)


"""
Rails
"""
central = network.nodes[0]
c0001 = network.addNodeFromCoordinates((0, 310))
c0002 = network.addNodeFromCoordinates((0, -40))
c0012 = network.addNodeFromCoordinates((0, -240))
c0003 = network.addNodeFromCoordinates((240, -240))
network.addTrack("TR-C0001", central, c0001)
network.addTrack("TR-C0001", central, c0001)
network.addTrack("TR-C0001", central, c0001)
network.addTrack("TR-C0001", central, c0001)
network.addTrack("TR-C0002", central, c0002)
network.addTrack("TR-C0012", central, c0012)
network.addTrack("TR-C0003", c0002, c0003)
for track in network.getTracks():
    print(track)
for node in network.getNodes():
    print(node)


"""
Trains
"""
train1 = network.addTrain("45003GH", central)
train1.addNodeToRoute(c0001)
train1.addNodeToRoute(central)

train2 = network.addTrain("766RHZ", central)
train2.addNodeToRoute(c0002)
train2.addNodeToRoute(c0003)


"""
Initial values
"""
if DARK_THEME:
    background = BACKGROUND_DARK
else:
    background = BACKGROUND_LIGHT


"""
Simulation
"""
pygame.init()
window = pygame.display.set_mode((1280, 720))
view = map.getView()
pygame.display.set_caption("Train Network Simulator")
running = True
start_time = time.time()
while running:
    clock.tick(30)

    key_state = controls.handle_events()
    if key_state.get(pygame.K_LEFT):
        view.position[0] += controls.pan_speed / view.zoom
    if key_state.get(pygame.K_RIGHT):
        view.position[0] -= controls.pan_speed / view.zoom
    if key_state.get(pygame.K_UP):
        view.position[1] += controls.pan_speed / view.zoom
    if key_state.get(pygame.K_DOWN):
        view.position[1] -= controls.pan_speed / view.zoom
    if key_state.get(pygame.K_PLUS):
        view.zoom = view.zoom + controls.zoom_speed
    if key_state.get(pygame.K_MINUS):
        view.zoom = view.zoom - controls.zoom_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic
    view.clamp()
    window.fill(background)

    # Map
    map.render(window, view)

    # Trains
    fps = clock.get_fps()
    if fps > 0:
        train1.drive(
            target_velocity=kmh_to_ms(180), speed_coefficient=GLOBAL_SPEED.value / fps
        )
        train2.drive(
            target_velocity=kmh_to_ms(100), speed_coefficient=GLOBAL_SPEED.value / fps
        )

    pygame.display.flip()

pygame.quit()
