"""Plan #24: torus + winding counter."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self, w): self.w = w
    def update(self, w): self.w = w
    def render_interface(self, f):
        import numpy as np
        if isinstance(f, np.ndarray):
            h,w=f.shape
            f[h-2,2] = min(15, self.w)
        return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d, px, py, gx, gy):
    return Level(sprites=[s["p"].clone().set_position(px,py), s["g"].clone().set_position(gx,gy)],
                 grid_size=(16,16), data={"difficulty":d})
levels = [lvl(i,2,8,14,8) for i in range(1,6)]
class Dn01(ARCBaseGame):
    def __init__(self):
        self._ui = U(0)
        super().__init__("dn01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._wind = 0
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
        if nx >= gw:
            nx, self._wind = 0, self._wind + 1
        elif nx < 0:
            nx = gw - 1
        if ny >= gh:
            ny = 0
        elif ny < 0:
            ny = gh - 1
        self._p.set_position(nx, ny)
        self._ui.update(self._wind)
        if self._p.x==self._g.x and self._p.y==self._g.y and self._wind>=2:
            self.next_level()
        self.complete_action()
