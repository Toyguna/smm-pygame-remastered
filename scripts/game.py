import pygame
import json
import os

import scripts.misc.world as world
import scripts.camera as camera
import scripts.util.time as time
import scripts.entity.player as player
import scripts.entity.enemy as enemy
import scripts.entity.powerup as powerup
import scripts.entity.coin as coin

# constants
WIDTH, HEIGHT = 1080, 720

SPRITESHEETS_PATH = "assets/resource/textures/spritesheets"
ICON_PATH = "assets/resource/icon.png"

ICON = pygame.image.load(ICON_PATH)

DEFAULT_BG_COLOR = (0, 80, 100)


def start():
    game = Game()
    game.start()


class Game:
    def __init__(self) -> None:
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SMM: Pygame Remastered")
        pygame.display.set_icon(ICON)

        self.clock = pygame.time.Clock()
        self.parser = world.SpriteSheetParser()
        self.worldparser = world.WorldParser()
        self.run = True

        self.world = self.worldparser.parse_world("w1")
        self.levelid = 1

        self.level_bg = self.world.get_level_bg(self.levelid)
        self.map = self.world.get_level_layout(self.levelid)
        self.map_collide, self.map_nocollide = self.world.optimize_level(self.map)

        self.tileset = "smb_map"
        self.objset = "smb_obj"
        
        self.tilesheet = self.parser.parse_tileset(f"{self.tileset}.png")
        self.objsheet = None
        self.camera = camera.Camera(self.window, (WIDTH, HEIGHT), self.tilesheet, False)

        self.player = player.Player(self.camera.tilesize, self.map_collide)
        self.entities = []


    def start(self):
        # initialize

        # start loop
        self.gameloop()

        # quit pygame
        pygame.quit()

    def gameloop(self):
        while self.run:

            # poll events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            # update
            self.update()
        
            # draw screen
            self.render()

    def render(self):
        self.window.fill((130, 130, 130))

        self.camera.render(self.map, self.level_bg)
        self.window.blit(self.camera.surface, self.camera.rect)

        # player
        self.window.blit(self.player.render(self.camera.tilesize), self.player.position)

        pygame.display.update()

    def update(self):
        time.update_dt(self.clock)
        self.player.update()

        self.cam_move()

    def set_level(self, id: int):
        self.levelid = id

        self.level_bg = self.world.get_level_bg(id)

        self.map = self.world.get_level_layout(id)
        self.map_collide, self.map_nocollide = self.world.optimize_level(self.map)

    def start_level(self):
        pass

    def update_spritesheets(self):
        self.camera.tilesheet = self.parser.parse_tileset(f'{self.tileset}.png')

    def cam_move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.camera.position.x += 10
        if keys[pygame.K_LEFT]:
            self.camera.position.x -= 10
        if keys[pygame.K_DOWN]:
            self.camera.position.y += 10
        if keys[pygame.K_UP]:
            self.camera.position.y -= 10

    # UTIL #
    def percent(self, value, percentage):
        return value * percentage / 100