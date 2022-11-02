import sys, math, os
from functools import wraps

try:
    import pygame
except:
    os.system('python -m pip install pygame')
    import pygame

from pygame.math import Vector2 as Vec2
pygame.init()
pygame.mixer.init()

# Memoisation
def memoise(func):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]
    return wrapper

def write(win, text, pos, size=32, colour=(244, 244, 244)):
    font = pygame.font.SysFont('freesanbold.ttf', size)
    text1 = font.render(str(text), True, colour)
    return text1

@memoise
def get_centre(surface):
    return Vec2(
        surface.get_width() * 0.5,
        surface.get_height() * 0.5
    )

mouse_pos = Vec2(0, 0)
timer_time = 25 * 60

class UiItem:
    def __init__(self, pos : Vec2):
        self.pos = pos
        pass
    def render(self, surface):
        pass
    def update(self, delta_time):
        pass
class Label(UiItem):
    def __init__(self, pos, text, text_size=32):
        UiItem.__init__(self, pos)
        self.text = text
        self.text_size = text_size
    def render(self, surface):
        write(surface, self.text, self.pos, size=self.text_size)
class Button(UiItem):
    def __init__(self, pos, text):
        UiItem.__init__(self, pos)
        self.hightlight = 0.0
        self.font_size = 100
        self.text = text
        self.text_surf = write(pygame.Surface((0, 0)), self.text, Vec2(-500, -500), self.font_size)
        self.padding = 50
        self.rounded = 50
        self.rect = pygame.Rect(pos.x - self.text_surf.get_width() * 0.5 - self.padding * 0.5, pos.y - self.text_surf.get_height() * 0.5 - self.padding * 0.5, self.text_surf.get_width() + self.padding, self.text_surf.get_height() + self.padding)
        self.action = lambda: print()
    def render(self, surface):
        self.text_surf = write(pygame.Surface((0, 0)), self.text, Vec2(-500, -500), self.font_size)
        self.rect = pygame.Rect(self.pos.x - self.text_surf.get_width() * 0.5 - self.padding * 0.5, self.pos.y - self.text_surf.get_height() * 0.5 - self.padding * 0.5, self.text_surf.get_width() + self.padding, self.text_surf.get_height() + self.padding)
        dims = Vec2(
            (self.text_surf.get_width() + self.padding),
            (self.text_surf.get_height() + self.padding)
        )
        pygame.draw.rect(surface, (150 * int(self.hightlight), 45, 110), pygame.Rect(self.pos.x - dims.x * 0.5, self.pos.y - dims.y * 0.5, dims.x, dims.y + 4), 0, self.rounded)
        pygame.draw.rect(surface, (155 * int(self.hightlight), 55, 125), pygame.Rect(self.pos.x - dims.x * 0.5, self.pos.y - dims.y * 0.5, dims.x, dims.y), 0, self.rounded)
        write(surface, self.text, self.pos - (dims * 0.5) + Vec2(self.padding * 0.5, self.padding * 0.5), self.font_size)
        surface.blit(self.text_surf, self.pos - (dims * 0.5) + Vec2(self.padding * 0.5, self.padding * 0.5))
    def update(self, delta_time):
        self.hightlight = 0.5
        if self.rect.collidepoint(mouse_pos):
            self.hightlight = 1.0
            if pygame.mouse.get_pressed()[0]:
                self.action()
                self.hightlight = 0.1
    def set_text(self, text):
        self.text = text
    def connect_action(self, act):
        self.action = act

class TimerButton(Button):
    def __init__(self, pos):
        Button.__init__(self, pos, "Aloita")
        self.padding = 50
        self.font_size = 300
        self.rounded = 75
        self.max_time = 0
        self.time = self.max_time
        self.connect_action(lambda:
            TimerButton.begin(self)
        )
    def update(self, delta_time):
        Button.update(self, delta_time)
        if self.time < 1:
            self.set_text("Aloita")
        else:
            self.set_text(
                str( math.floor(self.time / 60) ) + 'min ' + 
                str( round(self.time - (math.floor(self.time / 60) * 60)) ) + 's'
            )
        self.time -= delta_time
    def set_timeout_time(self, amt):
        self.max_time = amt
    def begin(self):
        self.time = 0
        if self.time < 1:
            self.time = self.max_time

class DropdownContainer(UiItem):
    def __init__(self, pos):
        UiItem.__init__(self, pos)
        self.children : list[UiItem] = []
        for c in range(len(self.children)):
            self.children[c].pos = Vec2(
                0,
                c * 32 + 32
            )
        self.height = 0
        self.rect = pygame.Rect(0, 0, 70, 32)
        self.surf = pygame.Surface((self.rect.w, self.rect.h))
    def render(self, surface):
        self.surf.fill((10, 7, 5))
        pygame.draw.rect(self.surf, (15, 12, 10), self.rect, 0, 5)

        pygame.draw.rect(self.surf, (20, 17, 15), (0, 0, 70, 28), 0, 5)
        pygame.draw.line(self.surf, (24, 24, 24), (10, 10), (70 * 0.5, 20), 4)
        pygame.draw.line(self.surf, (24, 24, 24), (60, 10), (70 * 0.5, 20), 4)

        for c in self.children:
            c.render(self.surf)
        surface.blit(self.surf, self.pos)
    def update(self, delta_time):
        self.height = 32
        if self.rect.collidepoint(mouse_pos):
            self.height = len(self.children) * 32 + 40
        self.rect.h += (self.height - self.rect.h) * 5 * delta_time
        self.surf = pygame.Surface((self.rect.w, self.rect.h))
        for c in self.children:
            c.update(delta_time)
    def add_child(self, obja):
        self.children.append(obja)
        for c in range(len(self.children)):
            self.children[c].pos = Vec2(
                0,
                c * 32 + 32
            )

class TimeSelectButton(UiItem):
    global timer_time
    def __init__(self, pos, time):
        UiItem.__init__(self, pos)
        self.time = time
        self.hithlight = 0.0
        self.rect = pygame.Rect(self.pos.x + 2, self.pos.y, 66, 28)
    def render(self, surface):
        global timer_time
        if timer_time == self.time * 60:
            pygame.draw.rect(surface, (int(47 * self.hithlight), int(37 * self.hithlight), int(53 * self.hithlight)), self.rect, 0, 6)
        else:
            pygame.draw.rect(surface, (int(20 * self.hithlight), int(17 * self.hithlight), int(15 * self.hithlight)), self.rect, 0, 6)
        surface.blit(write(surface, str(self.time) + 'min', self.pos + Vec2(5, 5), 30), self.pos + Vec2(5, 5))
    def update(self, delta_time):
        global timer_time
        self.rect = pygame.Rect(self.pos.x + 2, self.pos.y, 66, 28)
        self.hithlight = 1.0
        if self.rect.collidepoint(mouse_pos):
            self.hithlight = 1.3
            if pygame.mouse.get_pressed()[0]:
                self.hithlight = 1.1
                timer_time = self.time * 60


def main():
    global mouse_pos, timer_time
    pygame.display.set_caption('Naukio halloween')
    win = pygame.display.set_mode((1190, 600), pygame.RESIZABLE | pygame.SCALED)
    main_clock = pygame.time.Clock()
    FPS = 60
    run = True

    pygame.mixer.music.load('./song.mp3')
    pygame.mixer.music.play(1000)
    
    button = TimerButton(get_centre(win))
    button.set_timeout_time(timer_time)

    time_dropdown = DropdownContainer(Vec2(5, 5))
    time_dropdown.add_child(TimeSelectButton(Vec2(0, 0), 1))
    for i in range(8):
        time_dropdown.add_child(TimeSelectButton(Vec2(0, 0), 25 + (i * 5)))

    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
                break
        delta_time = main_clock.tick(FPS) / 1000
        button.set_timeout_time(timer_time)
        mouse_pos = pygame.mouse.get_pos()
        button.update(delta_time)
        time_dropdown.update(delta_time)
        win.fill((10, 7, 5))
        button.render(win)
        time_dropdown.render(win)
        pygame.display.flip()

if __name__ == '__main__':
    main()
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()
