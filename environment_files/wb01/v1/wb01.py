"""Plan #22: conveyor row of walls."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["beltwall"])}
s = spr()
ROW = 8
def lvl(d, xs, px, py, gx, gy):
    parts = [s["p"].clone().set_position(px,py), s["g"].clone().set_position(gx,gy)]
    for x in xs:
        parts.append(s["w"].clone().set_position(x,ROW))
    return Level(sprites=parts, grid_size=(16,16), data={"difficulty":d})
levels = [lvl(1,[4,5,6],2,8,14,8), lvl(2,[3,7,11],1,7,15,7), lvl(3,[2,6,10,14],0,8,15,6), lvl(4,[5,9],4,9,12,9), lvl(5,[1,4,7,10,13],2,6,14,10)]
class Wb01(ARCBaseGame):
    def __init__(self):
        super().__init__("wb01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._belts = [sp for sp in self.current_level._sprites if "beltwall" in sp.tags]
    def _shift(self):
        gw = self.current_level.grid_size[0]
        for sp in self._belts:
            sp.set_position((sp.x + 1) % gw, ROW)
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
            h = self.current_level.get_sprite_at(nx,ny,ignore_collidable=True)
            if not h or not h.is_collidable:
                self._p.set_position(nx,ny)
        self._shift()
        h2 = self.current_level.get_sprite_at(self._p.x,self._p.y,ignore_collidable=True)
        if h2 and h2.is_collidable and "beltwall" in h2.tags:
            self.lose(); self.complete_action(); return
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
