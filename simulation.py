import pygame
import controls
from network import RailNetwork
from trains import Train
import numpy as np
import clock

"""
Utility Methods
"""
BACKGROUND_LIGHT = (242, 242, 242)
BACKGROUND_DARK = (70, 70, 70)
DARK_THEME = True


def clamp(value, value_max, value_min):
    return max(min(value, value_max), value_min)


clock = pygame.time.Clock()
"""
Rails
"""
network = RailNetwork()
central = network.getNodes()[0]
c0001 = network.addNodeFromCoordinates((0, 310))
c0002 = network.addNodeFromCoordinates((0, -40))
c0012 = network.addNodeFromCoordinates((0, -240))
c0003 = network.addNodeFromCoordinates((240, -240))
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

train2 = network.addTrain("766RHZ", central)
train2.addNodeToRoute(c0002)
train2.addNodeToRoute(c0003)


"""
Initial values
"""
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Train Network Simulator")

if DARK_THEME:
    background = BACKGROUND_DARK
else:
    background = BACKGROUND_LIGHT

map_x = 640
map_y = 360
zoom = 1.0
pan_speed = 5
zoom_speed = 0.025


"""
Simulation
"""
pygame.init()

running = True
while running:
    clock.tick(30)

    key_state = controls.handle_events()
    if key_state.get(pygame.K_LEFT):
        map_x += pan_speed / zoom
    if key_state.get(pygame.K_RIGHT):
        map_x -= pan_speed / zoom
    if key_state.get(pygame.K_UP):
        map_y += pan_speed / zoom
    if key_state.get(pygame.K_DOWN):
        map_y -= pan_speed / zoom
    if key_state.get(pygame.K_PLUS):
        zoom = min(zoom + zoom_speed, 2.2)
    if key_state.get(pygame.K_MINUS):
        zoom = max(zoom - zoom_speed, 0.1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic

    # Map
    window.fill(background)
    map_x = clamp(map_x, 3600, -3600)
    map_y = clamp(map_y, 1800, -1800)
    map_pos = (map_x, map_y)

    # Rails
    network.draw(window, map_pos, zoom, dark_theme=DARK_THEME)

    # Trains
    train1.drive(target_velocity=180)
    train2.drive(target_velocity=100)
    pygame.display.flip()

pygame.quit()
