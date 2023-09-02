import pygame
import numpy
import os

import scripts.util.time as time

class Player:
    def __init__(self, tilesize: pygame.Vector2, collision_map: list) -> None:
        self.rect = pygame.Rect((0, 0), tilesize)

        self.position = pygame.Vector2(0, 0)
        self.world_pos = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.max_velocity = pygame.Vector2(12, 30)
        
        self.acceleration = tilesize.x * 0.2
        self.friction = tilesize.x * 0.1

        self.gravity_c = tilesize.y * 0.15
        self.min_jump = tilesize.y * 2
        self.max_jump = tilesize.y * 6
        self.run_jump_bonus = tilesize.y * 1
        self.on_ground = False

        self.collision_map = collision_map


        self.powerup = 0    # 0: None, 1: Big, 2: Fire
        self.star = 0

        self.lives = 3
        self.coins = 0
        self.score = 0


        self.sprites = {
            "0": {
                "Idle": pygame.image.load("assets/resource/icon.png").convert_alpha()
            }
        }


    def respawn(self, spawnpoint: pygame.Vector2):
        self.powerup = 0
        self.star = 0
        self.position = spawnpoint

    def update(self):
        self.movement()

    def render(self, tilesize: pygame.Vector2) -> pygame.Surface:
        return pygame.transform.scale(self.sprites["0"]["Idle"], tilesize)

    def animate(self):
        pass

    def movement(self):
        self.input()

        self.gravity()
        self.add_friction()
        self.limit_velocity()

        self.collision()

        self.apply_velocity()
        self.update_rect()

    def gravity(self):
        self.velocity.y += self.gravity_c * time.deltaTime

    def add_friction(self):
        if self.velocity.x < 0:
            if self.velocity.x + self.friction * time.deltaTime > 0:
                self.velocity.x = 0
            else:
                self.velocity.x += self.friction * time.deltaTime
                
        if self.velocity.x > 0:
            if self.velocity.x - self.friction * time.deltaTime < 0:
                self.velocity.x = 0
            else:
                self.velocity.x -= self.friction * time.deltaTime

    def apply_velocity(self):
        self.position += self.velocity

    def limit_velocity(self):
        print(time.deltaTime)

        if self.velocity.x > self.max_velocity.x:
            self.velocity.x = self.max_velocity.x
        if self.velocity.x < -self.max_velocity.x:
            self.velocity.x = -self.max_velocity.x

        if self.velocity.y > self.max_velocity.y:
            self.velocity.y = self.max_velocity.y

    def collision(self):
        # temporary
        if self.position.y + self.velocity.y > 500:
            self.position.y = 500
            self.velocity.y = 0
        #

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.velocity.x -= self.acceleration * time.deltaTime
        if keys[pygame.K_d]:
            self.velocity.x += self.acceleration * time.deltaTime

    def update_rect(self):
        self.rect.left = numpy.floor(self.position.x)
        self.rect.top = numpy.floor(self.position.y)