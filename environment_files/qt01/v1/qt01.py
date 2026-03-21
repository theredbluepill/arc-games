"""Plan #25: split/merge ghost positions."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "s": Sprite(pixels=[[7]], name="s", visible=True, collidable=False, tags=["split"]),
            "o": Sprite(pixels=[[10]], name="o", visible=True, collidable=False, tags=["observe"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(10,10), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5), s["s"].clone().set_position(3,5), s["o"].clone().set_position(6,5)]),
    lvl(2,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(8,8), s["s"].clone().set_position(2,2), s["o"].clone().set_position(7,7)]),
    lvl(3,[s["p"].clone().set_position(0,5), s["g"].clone().set_position(9,5), s["s"].clone().set_position(4,5), s["o"].clone().set_position(8,5)]),
    lvl(4,[s["p"].clone().set_position(2,3), s["g"].clone().set_position(7,6), s["s"].clone().set_position(3,4), s["o"].clone().set_position(6,5), s["w"].clone().set_position(5,5)]),
    lvl(5,[s["p"].clone().set_position(1,2), s["g"].clone().set_position(8,7), s["s"].clone().set_position(2,4), s["o"].clone().set_position(7,3)]),
]
class Qt01(ARCBaseGame):
    def __init__(self):
        super().__init__("qt01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._split = False
        self._gx = self._gy = None
    def _blocked(self, x, y):
        gw, gh = self.current_level.grid_size
        if not (0<=x<gw and 0<=y<gh):
            return True
        h = self.current_level.get_sprite_at(x,y,ignore_collidable=True)
        return h is not None and h.is_collidable and "wall" in h.tags
    def step(self):
        dx=dy=0
        v=self.action.id.value
        if v==1: dy=-1
        elif v==2: dy=1
        elif v==3: dx=-1
        elif v==4: dx=1
        else: self.complete_action(); return
        if not self._split:
            nx, ny = self._p.x+dx, self._p.y+dy
            if not self._blocked(nx,ny):
                self._p.set_position(nx,ny)
            hit = self.current_level.get_sprite_at(self._p.x,self._p.y,ignore_collidable=True)
            if hit and "split" in hit.tags:
                self._split = True
                self._gx, self._gy = self._p.x+1, self._p.y
            hit2 = self.current_level.get_sprite_at(self._p.x,self._p.y,ignore_collidable=True)
            if hit2 and "observe" in hit2.tags and self._split:
                self._split = False
                self._gx = self._gy = None
        else:
            nx, ny = self._p.x+dx, self._p.y+dy
            gx, gy = self._gx+dx, self._gy+dy
            b1, b2 = self._blocked(nx,ny), self._blocked(gx,gy)
            if b1 and b2:
                self.lose(); self.complete_action(); return
            if not b1:
                self._p.set_position(nx,ny)
            if not b2:
                self._gx, self._gy = gx, gy
            hit = self.current_level.get_sprite_at(self._p.x,self._p.y,ignore_collidable=True)
            if hit and "observe" in hit.tags:
                self._split = False
                self._gx = self._gy = None
        if self._p.x==self._g.x and self._p.y==self._g.y and not self._split:
            self.next_level()
        self.complete_action()
