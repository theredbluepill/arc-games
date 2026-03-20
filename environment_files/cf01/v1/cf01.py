"""Plan #8: fallow timer per cell."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d,parts,F):
    return Level(sprites=parts, grid_size=(10,10), data={"difficulty":d,"fallow":F})
levels = [lvl(1,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(8,8)],4),
          lvl(2,[s["p"].clone().set_position(0,0), s["g"].clone().set_position(9,9)],5),
          lvl(3,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(7,7)],3),
          lvl(4,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5)],4),
          lvl(5,[s["p"].clone().set_position(0,9), s["g"].clone().set_position(9,0)],5)]
class Cf01(ARCBaseGame):
    def __init__(self):
        super().__init__("cf01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._F = int(level.get_data("fallow"))
        self._last = {}
        self._t = 0
    def step(self):
        dx=dy=0
        v=self.action.id.value
        if v==1: dy=-1
        elif v==2: dy=1
        elif v==3: dx=-1
        elif v==4: dx=1
        else: self.complete_action(); return
        gw, gh = self.current_level.grid_size
        nx, ny = self._p.x+dx, self._p.y+dy
        if 0<=nx<gw and 0<=ny<gh:
            k = (nx,ny)
            if k in self._last and self._t - self._last[k] < self._F:
                self.lose(); self.complete_action(); return
            self._p.set_position(nx,ny)
            self._last[k] = self._t
        self._t += 1
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
