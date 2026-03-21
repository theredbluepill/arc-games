"""Plan #6: guard cone + scent grid."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self): pass
    def update(self): pass
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"]),
            "u": Sprite(pixels=[[8]], name="u", visible=True, collidable=False, tags=["guard"])}
s = spr()
def lvl(d,parts): return Level(sprites=parts, grid_size=(14,14), data={"difficulty":d})
levels = [lvl(1,[s["p"].clone().set_position(1,7), s["g"].clone().set_position(12,7), s["u"].clone().set_position(6,7)]),
          lvl(2,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(12,12), s["u"].clone().set_position(7,6), s["w"].clone().set_position(5,5)]),
          lvl(3,[s["p"].clone().set_position(0,7), s["g"].clone().set_position(13,7), s["u"].clone().set_position(8,7)]),
          lvl(4,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(11,11), s["u"].clone().set_position(6,4)]),
          lvl(5,[s["p"].clone().set_position(1,12), s["g"].clone().set_position(12,1), s["u"].clone().set_position(7,7)])]
class Sc01(ARCBaseGame):
    def __init__(self):
        super().__init__("sc01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4,5])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._gu = self.current_level.get_sprites_by_tag("guard")[0]
        gw, gh = level.grid_size
        self._sc = [[0.0]*gw for _ in range(gh)]
        self._mask = 0
    def _cone(self, px, py, gx, gy):
        return gy == py and px > gx
    def step(self):
        if self.action.id == GameAction.ACTION5:
            self._mask = 3
            self.complete_action(); return
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
                self._sc[self._p.y][self._p.x] += 2.0
                self._p.set_position(nx,ny)
        for y in range(gh):
            for x in range(gw):
                self._sc[y][x] *= 0.85
        if self._mask > 0:
            self._mask -= 1
        else:
            if self._cone(self._p.x,self._p.y,self._gu.x,self._gu.y) and self._sc[self._p.y][self._p.x] > 1.5:
                self.lose(); self.complete_action(); return
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
