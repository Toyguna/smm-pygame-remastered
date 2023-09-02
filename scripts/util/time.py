from pygame.time import Clock

deltaTime = 0

def update_dt(clock: Clock):
    global deltaTime

    deltaTime = clock.tick() / 1000