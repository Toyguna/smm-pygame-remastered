import pygame
import tkinter as tk
from tkinter import filedialog
import json
import os

import scripts.misc.world as world
import scripts.camera as camera
import scripts.util.time as time
import scripts.misc.ui as ui

# constants
WIDTH, HEIGHT = 1080, 720

SPRITESHEETS_PATH = "assets/resource/textures/spritesheets"
UI_PATH = "assets/resource/textures/ui"
ICON_PATH = "assets/resource/icon_editor.png"

ICON = pygame.image.load(ICON_PATH)

DEFAULT_BG_COLOR = (0, 80, 100)

# enum
STATE_EDITOR = 0
STATE_TILESET = 1

# init
pygame.font.init()

def start():
    editor = Editor()
    editor.start()

class Editor:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SMM: Pygame | Level Editor")
        pygame.display.set_icon(ICON)

        self.clock = pygame.time.Clock()
        self.parser = world.SpriteSheetParser()
        self.run = True

        self.tk = tk.Tk()
        self.tk.iconphoto(False, tk.PhotoImage(file = ICON_PATH))
        self.tk.withdraw()

        self.levelid = 1
        self.level_bg_color = [DEFAULT_BG_COLOR]

        self.world = []
        self.levelmap = []
        self.world_name = ""

        self.state = STATE_EDITOR
        self.selected_tile = 1

        self.tileset = "smb_map"
        self.objset = "smb_obj"
        
        self.tilesheet = self.parser.parse_tileset(f"{self.tileset}.png")
        self.camera = camera.Camera(self.window, (800, 600), self.tilesheet, True)

        self.tool = "brush"

        #   UI   #
        self.img_tools = {
            "brush": pygame.image.load(os.path.join(UI_PATH, "brush.png")),
            "erase": pygame.image.load(os.path.join(UI_PATH, "erase.png")),
            "bucket": pygame.image.load(os.path.join(UI_PATH, "bucket.png"))
        }

        self.img_buttons = {
            "file": pygame.image.load(os.path.join(UI_PATH, "button/file.png")),
            "import": pygame.image.load(os.path.join(UI_PATH, "button/import.png")),
            "export": pygame.image.load(os.path.join(UI_PATH, "button/export.png")),
            "new": pygame.image.load(os.path.join(UI_PATH, "button/new.png")),

            "brush": {
                "normal": pygame.image.load(os.path.join(UI_PATH, "button/brush_normal.png")),
                "selected": pygame.image.load(os.path.join(UI_PATH, "button/brush_selected.png"))
            },

            "erase": {
                "normal": pygame.image.load(os.path.join(UI_PATH, "button/erase_normal.png")),
                "selected": pygame.image.load(os.path.join(UI_PATH, "button/erase_selected.png"))
            },

            "bucket": {
                "normal": pygame.image.load(os.path.join(UI_PATH, "button/bucket_normal.png")),
                "selected": pygame.image.load(os.path.join(UI_PATH, "button/bucket_selected.png"))
            }
        }

        self.ui_selected = pygame.image.load(
                    os.path.join(UI_PATH, "selected_tile.png")
                ).convert_alpha()
        self.ui_cursor = pygame.image.load(
                os.path.abspath(os.path.join(UI_PATH, "cursor.png"))
            ).convert_alpha()


        self.font = pygame.font.SysFont("arial.ttf", 32)

        self.ui_tileset = 0
        self.tileset_txt = 0
        self.tileset_scroll = 0.0 # 1.0 - 0.0

        self.file_button = ui.UIButtonList(
            pygame.Vector2(800, 0),
            (96, 32),
            self.img_buttons["file"],
            [
                ui.UIButton(
                    pygame.Vector2(800, 32),
                    (80, 32),
                    self.img_buttons["import"]
                ),
                ui.UIButton(
                    pygame.Vector2(800, 64),
                    (80, 32),
                    self.img_buttons["export"]
                ),
                ui.UIButton(
                    pygame.Vector2(800, 96),
                    (80, 32),
                    self.img_buttons["new"]
                )           
            ]
        )
        self.file_button.toggle = True

    def start(self):
        # initialize
        self.create_tilemap()
        self.create_ui()

        # start loop
        self.gameloop()

        # quit pygame & tkinter
        pygame.quit()
        self.tk.destroy()

    def create_tilemap(self):
        self.levelmap = []

    def gameloop(self):
        while self.run:

            # poll events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                if event.type == pygame.MOUSEBUTTONUP:
                    self.select_tileset()
                    self.file_button.update()

                if event.type == pygame.MOUSEWHEEL:
                    self.zoom_camera(event.y)
                    self.scroll_tileset(event.y)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_TAB:
                        self.state = STATE_TILESET if self.state == STATE_EDITOR else STATE_EDITOR

                    if event.key == pygame.K_e:
                        self.tool = "erase"

                    if event.key == pygame.K_b:
                        self.tool = "brush"

                    if event.key == pygame.K_RIGHT:
                        self.set_level(self.levelid + 1)
                        
                    if event.key == pygame.K_LEFT:
                        self.set_level(self.levelid - 1)


            # update
            time.update_dt(self.clock)

            # handle logic
            self.move_camera()
            self.handle_tools()
            self.handle_buttons()

            # draw screen
            self.render()

    def render(self):
        self.window.fill((130, 130, 130))

        self.camera.render(self.levelmap, self.level_bg_color[self.levelid - 1])
        self.show_cursor()
        self.window.blit(self.camera.surface, self.camera.rect)

        self.draw_ui()

        pygame.display.update()

    
    def move_camera(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.camera.position.y -= 5 * self.camera.zoom / (self.window.get_size()[1] / self.camera.size[1])
        if keys[pygame.K_a]:
            self.camera.position.x -= 5 * self.camera.zoom / (self.window.get_size()[0] / self.camera.size[0])
        if keys[pygame.K_s]:
            self.camera.position.y += 5 * self.camera.zoom / (self.window.get_size()[1] / self.camera.size[1])
        if keys[pygame.K_d]:
            self.camera.position.x += 5 * self.camera.zoom / (self.window.get_size()[0] / self.camera.size[0])

        if self.camera.position.x < 0: self.camera.position.x = 0
        if self.camera.position.y < 0: self.camera.position.y = 0

    def zoom_camera(self, y: int):
        if self.state != STATE_EDITOR: return

        self.camera.zoom += 0.1 * y

        if self.camera.zoom > 2: self.camera.zoom = 2
        if self.camera.zoom < 0.1: self.camera.zoom = 0.1

        self.camera.calculate_tilesize()

    def b_export(self):
        print("Exporting...")

        filedata = filedialog.asksaveasfile(filetypes=[("JSON file", "*.json")], defaultextension="*.*")

        if filedata is None:
            print(f"Operation 'export' canceled.")
            return
        
        self.save_level()

        path = filedata.name

        data = {
            "name": os.path.splitext(os.path.basename(path))[0],
            "tileset": self.tileset,
            "objset": self.objset,

            "levels": {

            }
        }

        for i, v in enumerate(self.world):
            lvldata = {
                "background-color": self.level_bg_color[i],
                "layout": v
            }

            #if i + 1 > len(self.level_bg_color):
            #    lvldata["background-color"] = DEFAULT_BG_COLOR
            #else:
            #    lvldata["background-color"] = self.level_bg_color[i]

            data["levels"][str(i + 1)] = lvldata

        converted_json = json.dumps(data)

        filedata.write(converted_json)
        filedata.close()

        print(f"Successfully exported to '{path}'!")

    def b_import(self):
        print("Importing...")

        filedata = filedialog.askopenfile(filetypes=[("JSON file", "*.json")], defaultextension="*.*")

        if filedata is None:
            print(f"Operation 'import' canceled.")
            return
        
        path = filedata.name

        try:
            world_data = json.loads(filedata.read())
        except json.decoder.JSONDecodeError:
            print(f"Operation 'import' canceled: JSON file is empty.")
            return
        
        
        self.world = []
        self.level_bg_color = []
        self.levelmap = []

        self.tileset = f'{world_data["tileset"]}'
        self.objset = f'{world_data["objset"]}'
        self.world_name = world_data["name"]

        for v in world_data["levels"]:
            self.level_bg_color.append(world_data["levels"][v]["background-color"])
            self.world.append(world_data["levels"][v]["layout"])

        self.update_spritesheets()
        
        self.levelmap = self.world[0]
        self.levelid = 1

        filedata.close()

        print(f"Successfully imported from '{path}' !")

    def b_new(self):
        print("Creating a new world...")

        self.world = []
        self.level_bg_color = [DEFAULT_BG_COLOR]
        self.levelmap = []
        self.levelid = 1

        self.tileset = "smb_map"
        self.objset = "smp_obj"

        print("A new world was created successfully!")

        self.update_spritesheets()

    def update_spritesheets(self):
        self.camera.tilesheet = self.parser.parse_tileset(f'{self.tileset}.png')

    def set_level(self, id: int):
        if id < 1:
            return
        
        self.save_level()

        if id > len(self.world):
            self.new_level()

        self.levelmap = self.world[id - 1]
        self.levelid = id

    def new_level(self):
        self.world.append([])
        self.level_bg_color.append(DEFAULT_BG_COLOR)

    def save_level(self):
        if self.levelid > len(self.world):
            self.world.append(self.levelmap)
        else:
            self.world[self.levelid - 1] = self.levelmap

    # TOOLS #
    def handle_tools(self):
        if not self.camera.rect.collidepoint(pygame.mouse.get_pos()): return
        if self.state != STATE_EDITOR: return

        mbuttons = pygame.mouse.get_pressed()

        if (mbuttons[0]):
            match self.tool:
                case "brush":
                    self.brush_tool()
                case "erase":
                    self.erase_tool()
    
    def brush_tool(self):
        mouse = pygame.mouse.get_pos()
        n_mouse = (
            mouse[0] - self.camera.camera_position[0] + self.camera.position.x, 
            mouse[1] - self.camera.camera_position[1] + self.camera.position.y
        )

        gridx = int(n_mouse[0] // self.camera.tilesize[0]) + 1
        gridy = int(n_mouse[1] // self.camera.tilesize[1]) + 1

        map_len = len(self.levelmap)

        # create rows if absent
        if gridy > map_len:
            for i in range(gridy - map_len):
                self.levelmap.append([])

        row_len = len(self.levelmap[gridy - 1])

        # create columns if absent
        if gridx > row_len:
            for i in range(gridx - row_len):
                self.levelmap[gridy - 1].append(0)

        # place tiles
        self.levelmap[gridy - 1][gridx - 1] = self.selected_tile

    def erase_tool(self):
        mouse = pygame.mouse.get_pos()
        n_mouse = (
            mouse[0] - self.camera.camera_position[0] + self.camera.position.x, 
            mouse[1] - self.camera.camera_position[1] + self.camera.position.y
        )

        gridx = int(n_mouse[0] // self.camera.tilesize[0]) + 1
        gridy = int(n_mouse[1] // self.camera.tilesize[1]) + 1

        map_len = len(self.levelmap)

        # create rows if absent
        if gridy > map_len:
            for i in range(gridy - map_len):
                self.levelmap.append([])

        row_len = len(self.levelmap[gridy - 1])

        # create columns if absent
        if gridx > row_len:
            for i in range(gridx - row_len):
                self.levelmap[gridy - 1].append(0)

        # place tiles
        self.levelmap[gridy - 1][gridx - 1] = 0

    # UI #
    def create_ui(self):
        w, h = self.window.get_size()

        # TILESET #
        self.ui_tileset = ui.UIElement(
            pygame.Rect(
            self.percent(w, 10), self.percent(h, 10),
            self.percent(w, 80), self.percent(h, 80)
            )
        )

        self.tileset_txt = self.font.render("TILESET", True, (255, 255, 255))

        self.ui_tileset.background_color = (30, 30, 30)
        self.ui_tileset.border_color = (50, 50, 50)
        self.ui_tileset.border_px = 5

        self.ui_tileset.update_border()

    def update_ui(self):
        self.handle_buttons()

    def draw_ui(self):
        self.ui_position()
        self.ui_level()

        self.file_button.draw(self.window)

        # TILESET #
        self.draw_tileset()
            
    def draw_tileset(self):
        if self.state != STATE_TILESET: return

        self.ui_tileset.render(self.window)
        self.window.blit(self.tileset_txt, 
            (
                self.ui_tileset.surface.get_width() / 2 + self.tileset_txt.get_width() / 2,
                self.ui_tileset.rect.top + 15
            )           
        )

        size = self.ui_tileset.rect.width / 20
        set_height = size * len(self.camera.tilesheet) / 20

        right = self.ui_tileset.rect.right
        left = self.ui_tileset.rect.left
        top = self.ui_tileset.rect.top
        bottom = self.ui_tileset.rect.bottom

        scroll_speed = 400
        offset = self.tileset_scroll * scroll_speed

        if offset > set_height:
            offset = set_height

            self.tileset_scroll = offset / scroll_speed

        x, y = left + size / 2, top + 60 - offset

        for tile in self.camera.tilesheet:
            if (x > right - size / 2):
                x = left + size / 2
                y += size

            if y < top + size or y > bottom - size: 
                x += size
                continue

            self.window.blit(pygame.transform.scale(tile, (size, size))
                             , (x, y))
            
            # selected tile
            if tile == self.camera.tilesheet[self.selected_tile - 1]: 
                self.window.blit(pygame.transform.scale(self.ui_selected, (size, size))
                             , (x, y))
            
            x += size

    def scroll_tileset(self, y):
        if self.state != STATE_TILESET: return

        self.tileset_scroll -= 0.1 * y

        if self.tileset_scroll < 0: self.tileset_scroll = 0

    def select_tileset(self):
        if self.state != STATE_TILESET: return
        
        size = self.ui_tileset.rect.width / 20
        set_height = size * len(self.camera.tilesheet) / 20

        right = self.ui_tileset.rect.right
        left = self.ui_tileset.rect.left
        top = self.ui_tileset.rect.top
        bottom = self.ui_tileset.rect.bottom

        scroll_speed = 400
        offset = self.tileset_scroll * scroll_speed

        if offset > set_height:
            offset = set_height

            self.tileset_scroll = offset / scroll_speed

        x, y = left + size / 2, top + 60 - offset

        for tile in self.camera.tilesheet:
            if (x > right - size / 2):
                x = left + size / 2
                y += size

            if y < top + size or y > bottom - size: 
                x += size
                continue
        
            if pygame.Rect(x, y, size, size).collidepoint(pygame.mouse.get_pos()):
                self.selected_tile = self.camera.tilesheet.index(tile) + 1

            x += size

    def handle_buttons(self):
        self.file_button.update_buttons()

        if self.file_button.buttons[0].clicked():
            self.file_button.click = False
            self.file_button.buttons[0].click = False
            self.b_import()

        if self.file_button.buttons[1].clicked():
            self.file_button.click = False
            self.file_button.buttons[1].click = False
            self.b_export()

        if self.file_button.buttons[2].clicked():
            self.file_button.click = False
            self.file_button.buttons[2].click = False
            self.b_new()


    def show_cursor(self):
        if self.state != STATE_EDITOR: return

        mouse = pygame.mouse.get_pos()

        img_rect = self.ui_cursor.get_rect()
        img_rect.size = self.camera.tilesize
        img_rect.left = mouse[0]
        img_rect.top = mouse[1]

        if (not self.camera.rect.colliderect(img_rect)): return

        img = pygame.transform.scale(self.ui_cursor, self.camera.tilesize)
        n_mouse = (
            mouse[0] - self.camera.camera_position[0] + self.camera.position.x, 
            mouse[1] - self.camera.camera_position[1] + self.camera.position.y
        )

        grid_mouse = (
            n_mouse[0] // self.camera.tilesize[0] * self.camera.tilesize[0] - self.camera.position.x,
            n_mouse[1] // self.camera.tilesize[1] * self.camera.tilesize[1] - self.camera.position.y
        )

        # tile
        if self.tool == "brush":
            tile = pygame.Surface.copy(self.camera.tilesheet[self.selected_tile - 1])
            tile.set_alpha(100)
            self.camera.surface.blit(pygame.transform.scale(tile, self.camera.tilesize), grid_mouse)

        # cursor
        self.camera.surface.blit(img, grid_mouse)

        tool = pygame.transform.scale(self.img_tools[self.tool], (32, 32))
        self.camera.surface.blit(tool, (n_mouse[0] - self.camera.position.x, n_mouse[1] - self.camera.position.y))

    def ui_position(self):
        text = self.font.render(f"({int(self.camera.position[0])}, {int(self.camera.position[1])})", True, (255, 255, 255))

        self.window.blit(text, (10, 10))

    def ui_level(self):
        text = self.font.render(f"Level: {self.levelid}", True, (255, 255, 255))

        self.window.blit(text, (10, 50)) 

    # UTIL #
    def percent(self, value, percentage):
        return value * percentage / 100
