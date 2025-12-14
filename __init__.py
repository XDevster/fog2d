import sys
import time
import math
from colorama import Fore, Back, Style, init

init()

WIDTH, HEIGHT = 40, 20
FPS = 30

def cursor(x, y):
    sys.stdout.write(f"\033[{y+1};{x+1}H")

def clear():
    sys.stdout.write("\033[2J")

def splash():
    clear()
    logo = [
        "███████╗ ██████╗  ██████╗ ██████╗ ██████╗ ",
        "██╔════╝██╔═══██╗██╔════╝╚════██╗██╔══██╗",
        "█████╗  ██║   ██║██║  ███╗ █████╔╝██║  ██║",
        "██╔══╝  ██║   ██║██║   ██║██╔═══╝ ██║  ██║",
        "██║     ╚██████╔╝╚██████╔╝███████╗██████╔╝",
        "╚═╝      ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ",
        "",
	"Fog2D Engine  fog2d.rf.gd"
    ]
    y = HEIGHT // 2 - len(logo) // 2
    for line in logo:
        cursor(WIDTH // 2 - len(line) // 2, y)
        sys.stdout.write(Fore.WHITE + Style.BRIGHT + line)
        y += 1
    sys.stdout.flush()
    time.sleep(2)
    clear()

class Renderer:
    def __init__(self):
        self.front = {}
        self.back = {}

    def draw(self, x, y, ch, color):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.back[(x, y)] = (ch, color)

    def present(self):
        for pos, data in self.back.items():
            if self.front.get(pos) != data:
                cursor(pos[0], pos[1])
                sys.stdout.write(data[1] + data[0] + Style.RESET_ALL)
        self.front = self.back.copy()
        self.back.clear()
        sys.stdout.flush()


class Collider:
    def __init__(self, solid=True):
        self.solid = solid

class CollisionSystem:
    def resolve(self, entities):
        occupied = {}
        for e in entities:
            if e.collider and e.collider.solid:
                occupied[(e.x, e.y)] = e
        return occupied


class Light:
    def __init__(self, radius=5, intensity=1.0):
        self.radius = radius
        self.intensity = intensity

class LightSystem:
    def light_at(self, x, y, lights):
        value = 0
        for l, lx, ly in lights:
            d = math.dist((x, y), (lx, ly))
            if d < l.radius:
                value += (1 - d / l.radius) * l.intensity
        return min(value, 1.0)

try:
    import msvcrt
    def default_get_key():
        if msvcrt.kbhit():
            return msvcrt.getch().decode().lower()
        return None
except ImportError:
    def default_get_key():
        return None

class InputSystem:
    def __init__(self):
        self.get_key = default_get_key
        self.pressed = set()

    def update(self):
        key = self.get_key()
        if key:
            self.pressed.add(key)

    def is_pressed(self, key):
        return key.lower() in self.pressed

    def clear(self):
        self.pressed.clear()

class Entity:
    def __init__(self, x, y, char="█", color=Back.WHITE):
        self.x, self.y = x, y
        self.char = char
        self.color = color
        self.collider = None
        self.light = None


class Scene:
    def __init__(self, renderer):
        self.renderer = renderer
        self.entities = []
        self.collision = CollisionSystem()
        self.light_system = LightSystem()

    def add(self, entity):
        self.entities.append(entity)

    def update(self):
        self.collision.resolve(self.entities)

    def render(self):
        lights = [(e.light, e.x, e.y) for e in self.entities if e.light]
        for e in self.entities:
            brightness = self.light_system.light_at(e.x, e.y, lights)
            color = e.color
            if brightness < 0.2:
                color = Back.BLACK
            elif brightness < 0.5:
                color = Back.BLUE
            self.renderer.draw(e.x, e.y, e.char, color)


class Fog2D:
    def __init__(self):
        splash()
        self.renderer = Renderer()
        self.scene = Scene(self.renderer)
        self.input = InputSystem()
        clear()

    def run(self):
        while True:
            self.input.update()
            self.scene.update()
            self.scene.render()
            self.renderer.present()
            self.input.clear()
            time.sleep(1 / FPS)


if __name__ == "__main__":
    engine = Fog2D()
    engine.run()
