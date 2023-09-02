import pygame

class UIElement:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.surface = pygame.Surface(rect.size)

        self.background_color = (255, 255, 255)
        self.border_color = (255, 255, 255)

        self.border_px = 0

        self.border = pygame.Rect(
            self.rect.left - self.border_px,
            self.rect.top - self.border_px,
            self.rect.right + self.border_px,
            self.rect.bottom + self.border_px,
        )

        self.children = []
        
    def render(self, window: pygame.Surface):
        self.surface.fill(self.background_color)
        
        if self.border_px != 0:
            pygame.draw.rect(window, self.border_color, self.border)

        for child in self.children:
            self.surface.blit(child.surface, child.rect)

        window.blit(self.surface, self.rect)

    def update_border(self):
        self.border = pygame.Rect(
            self.rect.left - self.border_px,
            self.rect.top - self.border_px,
            self.rect.width + self.border_px * 2,
            self.rect.height + self.border_px * 2,
        )

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)


class UIImage(UIElement):
    def __init__(self, rect: pygame.Rect, path: str) -> None:
        super().__init__(rect)

        self.path = path

        self.image = pygame.image.load(path).convert_alpha()

    
    def render(self):
        self.surface.blit(self.image)


class UIButton:
    def __init__(self, pos: pygame.Vector2, scale: pygame.Vector2, img: pygame.Surface) -> None:
        self.pos = pos
        self.scale = scale
        self.img = img

        self.active = True
        self.click = False

    def clicked(self):
        return self.click
    
    def update(self):
        if not self.active: return

        mouse = pygame.mouse.get_pos()
        m1 = pygame.mouse.get_pressed()[0]
        size = self.scale

        if size is None:
            size = self.img.get_size()

        rect = pygame.Rect(self.pos, size)

        self.click = rect.collidepoint(mouse) and m1

    def draw(self, surface: pygame.Surface):
        if not self.active: return

        if self.scale is not None:
            surface.blit(pygame.transform.scale(self.img, self.scale), self.pos)
        else:
            surface.blit(self.img, self.pos)


class UIButtonList(UIButton):
    def __init__(self, pos: pygame.Vector2, scale: pygame.Vector2, img: pygame.Surface, buttons: list[UIButton]) -> None:
        super().__init__(pos, scale, img)
        self.background = True
        self.background_color = (40, 40, 40)

        self.buttons = buttons

        self.toggle = False

        self.active = True
        self.click = False

    def draw(self, surface: pygame.Surface):
        if not self.active: return

        if self.scale is not None:
            surface.blit(pygame.transform.scale(self.img, self.scale), self.pos)
        else:
            surface.blit(self.img, self.pos)

        if self.click:
            for button in self.buttons:
                button.draw(surface)

    def update(self):
        if not self.active: return

        mouse = pygame.mouse.get_pos()
        size = self.scale

        if size is None:
            size = self.img.get_size()

        rect = pygame.Rect(self.pos, size)

        if rect.collidepoint(mouse):
            if self.toggle:
                self.click = not self.click
            else:
                self.click = rect.collidepoint(mouse)

    def update_buttons(self):
        if not self.active or not self.click: return

        for btn in self.buttons:
            btn.update()