"""Plan #23: tumbler combo."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "d": Sprite(pixels=[[3]], name="d", visible=True, collidable=True, tags=["door"])}
s = spr()
def lvl(d, t0, t1, t2):
    return Level(sprites=[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5), s["d"].clone().set_position(5,5)],
                 grid_size=(10,10), data={"difficulty":d,"target":[t0,t1,t2]})
levels = [lvl(1,2,3,1), lvl(2,1,1,4), lvl(3,0,5,2), lvl(4,3,3,3), lvl(5,4,2,0)]
class Lk01(ARCBaseGame):
    def __init__(self):
        super().__init__("lk01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        ds = self.current_level.get_sprites_by_tag("door")
        self._door = ds[0] if ds else None
        self._t = [0, 0, 0]
        self._tar = list(level.get_data("target"))
    def step(self):
        v = self.action.id.value
        if self._door is not None:
            if v == 1:
                self._t[0] = (self._t[0] + 1) % 6
            elif v == 2:
                self._t[1] = (self._t[1] + 1) % 6
            elif v == 3:
                self._t[2] = (self._t[2] + 1) % 6
            if self._t == self._tar and self._door in self.current_level._sprites:
                self.current_level.remove_sprite(self._door)
                self._door = None
        else:
            dx = dy = 0
            if v == 1:
                dy = -1
            elif v == 2:
                dy = 1
            elif v == 3:
                dx = -1
            elif v == 4:
                dx = 1
            gw, gh = self.current_level.grid_size
            nx, ny = self._p.x + dx, self._p.y + dy
            if 0 <= nx < gw and 0 <= ny < gh:
                hit = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
                if not hit or not hit.is_collidable:
                    self._p.set_position(nx, ny)
        if self._p.x == self._g.x and self._p.y == self._g.y:
            self.next_level()
        self.complete_action()
