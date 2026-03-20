"""Plan #20: beat-gated moves."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self, t): self.t = t
    def update(self, t): self.t = t
    def render_interface(self, f):
        import numpy as np
        if isinstance(f, np.ndarray):
            h,w=f.shape
            f[h-2,2] = 14 if self.t % 3 == 0 else 2
        return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d,parts,B=3):
    return Level(sprites=parts, grid_size=(11,11), data={"difficulty":d,"beat":B})
levels = [lvl(i,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(9,5)]) for i in range(1,6)]
class Rb01(ARCBaseGame):
    def __init__(self):
        self._ui = U(0)
        super().__init__("rb01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._B = int(level.get_data("beat") or 3)
        self._t = 0
    def step(self):
        dx=dy=0
        v=self.action.id.value
        if v==1: dy=-1
        elif v==2: dy=1
        elif v==3: dx=-1
        elif v==4: dx=1
        else: self.complete_action(); return
        self._t += 1
        self._ui.update(self._t)
        if self._t % self._B != 0:
            self.complete_action(); return
        gw, gh = self.current_level.grid_size
        nx, ny = self._p.x+dx, self._p.y+dy
        if 0<=nx<gw and 0<=ny<gh:
            h = self.current_level.get_sprite_at(nx,ny,ignore_collidable=True)
            if not h or not h.is_collidable:
                self._p.set_position(nx,ny)
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
