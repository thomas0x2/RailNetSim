import pygame
import numpy as np
import view.map_view as map_view
import view.window_view as window_view

pan_speed = 10
zoom_speed = 0.025
left_mouse_button_pressed = False
right_mouse_button_pressed = False
init_mouse_pos = None
prev_mouse_pos = None


def handle_view_controls(view, key_state):
    """
    Handles the view controls.
    """
    global pan_speed, zoom_speed

    if key_state.get(pygame.K_LEFT):
        view.position[0] += pan_speed / view.zoom
    if key_state.get(pygame.K_RIGHT):
        view.position[0] -= pan_speed / view.zoom
    if key_state.get(pygame.K_UP):
        view.position[1] += pan_speed / view.zoom
    if key_state.get(pygame.K_DOWN):
        view.position[1] -= pan_speed / view.zoom
    if key_state.get(pygame.K_PLUS):
        view.zoom = view.zoom + zoom_speed
    if key_state.get(pygame.K_MINUS):
        view.zoom = view.zoom - zoom_speed


def handle_mouse_input(map_view, window_view):
    global left_mouse_button_pressed
    global right_mouse_button_pressed
    global init_mouse_pos
    global prev_mouse_pos

    mouse_position = get_cursor_position()
    if pygame.mouse.get_pressed()[0] and not left_mouse_button_pressed:
        left_mouse_button_pressed = True
        init_mouse_pos = mouse_position
        prev_mouse_pos = init_mouse_pos
    elif pygame.mouse.get_pressed()[0] and left_mouse_button_pressed:
        if prev_mouse_pos is not None:
            relative_movement = mouse_position - prev_mouse_pos
            window_view.drag_window(mouse_position, relative_movement)
        prev_mouse_pos = mouse_position
    elif not pygame.mouse.get_pressed()[0] and left_mouse_button_pressed:
        left_mouse_button_pressed = False
        map_view.handle_node_collision(window_view, mouse_position, left=True)
        window_view.handle_window_collision(mouse_position)

    if pygame.mouse.get_pressed()[2] and not right_mouse_button_pressed:
        right_mouse_button_pressed = True
    elif not pygame.mouse.get_pressed()[2] and right_mouse_button_pressed:
        right_mouse_button_pressed = False
        map_view.handle_node_collision(window_view, mouse_position, left=False)


def get_cursor_position():
    return np.array(pygame.mouse.get_pos())
