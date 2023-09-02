import pygame
from PIL import Image
import os
import json

TILESET_PATH = "assets/resource/textures/spritesheets/tileset"
OBJSET_PATH = "assets/resource/textures/spritesheets/objset"
WORLDS_PATH = "assets/worlds"

class SpriteSheetParser:
    def __init__(self) -> None:
        pass

    def parse_tileset(self, name: str) -> list:
        tileset = []

        path = os.path.abspath(os.path.join(TILESET_PATH, name))
        image = Image.open(path)

        tilesize = 16

        for y in range(image.height // tilesize):
            for x in range(image.width // tilesize):
                tile = image.crop(
                    (
                        x * tilesize,
                        y * tilesize,
                        x * tilesize + tilesize,
                        y * tilesize + tilesize
                    )
                )

                sprite = pygame.image.frombytes(tile.tobytes(), tile.size, tile.mode)
                tileset.append(sprite)
        
        return tileset
    

    def parse_objset(self, name: str) -> dict:
        # must be hardcoded
        # returns a dict

        objset = {}

        return objset

class World:
    def __init__(self, name: str, tileset: str, objset: str, levels: dict) -> None:
        self.name = name
        self.tileset = tileset
        self.objset = objset

        self.levels = levels
        self.length = len(levels)

    def get_level(self, id: int):
        if id > self.length:
            return None
        
        return self.levels[str(id)]
    
    def get_level_layout(self, id):
        return self.levels[str(id)]["layout"]
    
    def get_level_bg(self, id):
        return self.levels[str(id)]["background-color"]

    def optimize_level(self, level_layout: list) -> tuple[list, list]:
        """
            Seperates a level layout to:\n
                [0] Blocks that will interact with the player.\n
                [1] Blocks that will never interact with the player.\n
            ``-> tuple[list, list]``
        """

        collidable = []     # (tile_id, x, y)
        non_collidable = []     # (tile_id, x, y)

        for y, vy in enumerate(level_layout):
            for x, vx in enumerate(vy):
                if vx == 0: continue
                
                # Get surrounding blocks

                # None = out of bounds
                # True = block in direction
                # False = air
                top, left, right, down = None, None, None, None

                #    [u]
                # [l] c [r]
                #    [d]
                #
                #   u = y - 1
                #   l = x - 1
                #   r = x + 1
                #   d = x + 1

                
                # check valid spots
                if y - 1 >= 0 and len(level_layout[y - 1]) > x:
                    top = level_layout[y - 1][x] != 0
                else:
                    top = False
                    
                if y + 1 < len(level_layout) and len(level_layout[y + 1]) > x:
                    down = level_layout[y + 1][x] != 0
                else:
                    down = False

                if x - 1 >= 0:
                    left = level_layout[y][x - 1] != 0
                else:
                    left = False

                if x + 1 < len(vy):
                    right = level_layout[y][x + 1] != 0
                else:
                    right = False

                if False in [top, left, right, down]:
                    collidable.append(
                        (level_layout[y][x], x, y)
                        )
                else:
                    non_collidable.append(
                        (level_layout[y][x], x, y)
                        )
                    

        return (collidable, non_collidable)


class WorldParser:
    def __init__(self) -> None:
        pass

    def parse_world(self, world_name: str) -> World:
        filedata = open(os.path.join(WORLDS_PATH, f"{world_name}.json"), "r")

        try:
            world_data = json.loads(filedata.read())
        except json.decoder.JSONDecodeError:
            print(f"Could not read world file: JSON file is empty.")
            return
        
        name = world_data["name"]
        tileset = world_data["tileset"]
        objset = world_data["objset"]
        levels = world_data["levels"]
        
        world = World(name, tileset, objset, levels)

        return world
    