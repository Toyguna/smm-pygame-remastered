import pygame


class Camera:
    def __init__(self, window: pygame.Surface, size: tuple[int, int], tilesheet: list, editor: bool) -> None:
        self.window = window
        self.ratio = (1, 1)

        self.position = pygame.Vector2(0, 0)

        self.camera_position = (0, 0)
        self.size = size #self.window.get_size()
        self.rect = pygame.Rect(self.camera_position, self.size)
        self.surface = pygame.Surface(self.size)

        self.zoom = 0.5

        self.tilesize = pygame.Vector2(16, 16)
        self.tilesheet = tilesheet

        self.editor = editor
        
        self.calculate_tilesize()


    def calculate_tilesize(self):
        width, height = self.size

        self.tilesize.x = width / (self.ratio[0] * 10 / self.zoom)
        self.tilesize.y = height / (self.ratio[1] * 10 / self.zoom)

    def set_tilesheet(self, tilesheet: list):
        self.tilesheet = tilesheet


    def draw_map(self, map: list):
        for y, vy in enumerate(map):
            for x, vx in enumerate(vy):
                if (vx == 0): continue

                pos = (
                    x * self.tilesize.x - self.position.x,
                    y * self.tilesize.y - self.position.y
                )

                # dont draw if not visible
                if (
                    pos[0] + self.tilesize.x + 5 < 0 or
                    pos[0] - 5 > self.size[0] 
                    or
                    pos[1] + self.tilesize.y * 2 + 5 < 0 or
                    pos[1] - 5 > self.size[1]
                ): continue

                img = pygame.transform.scale(self.tilesheet[vx-1], self.tilesize)

                self.surface.blit(img, pos)

    def debug_draw(self, nocollide, collide):
        for tile in nocollide:
            x, y = tile[1:]

            pos = (
                    x * self.tilesize.x - self.position.x,
                    y * self.tilesize.y - self.position.y
            )

                # dont draw if not visible
            if (
                pos[0] + self.tilesize.x + 5 < 0 or
                pos[0] - 5 > self.size[0] 
                or
                pos[1] + self.tilesize.y * 2 + 5 < 0 or
                pos[1] - 5 > self.size[1]
            ): continue


            pygame.draw.rect(self.surface, (255, 0, 0), 
                             pygame.Rect(pos, self.tilesize))

        for tile in collide:
            x, y = tile[1:]

            pos = (
                    x * self.tilesize.x - self.position.x,
                    y * self.tilesize.y - self.position.y
            )

                # dont draw if not visible
            if (
                pos[0] + self.tilesize.x + 5 < 0 or
                pos[0] - 5 > self.size[0] 
                or
                pos[1] + self.tilesize.y * 2 + 5 < 0 or
                pos[1] - 5 > self.size[1]
            ): continue


            pygame.draw.rect(self.surface, (0, 255, 0), 
                             pygame.Rect(pos, self.tilesize))

    def render(self, map: list, bg: tuple[int, int, int]):
        self.surface.fill(bg)

        self.draw_map(map)