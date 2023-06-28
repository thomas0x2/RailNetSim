import pygame

key_state = {}


def handle_events():
    global key_state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        elif event.type == pygame.KEYDOWN:
            key_state[event.key] = True
        elif event.type == pygame.KEYUP:
            key_state[event.key] = False

    return key_state
