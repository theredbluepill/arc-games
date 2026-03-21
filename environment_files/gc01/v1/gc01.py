"""Plan #29: non-lethal spreading coral."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "c": Sprite(pixels=[[13]], name="c", visible=True, collidable=True, tags=["coral"])}
s = spr()
def lvl(d, M, parts):
    return Level(sprites=parts, grid_size=(14,14), data={"difficulty":d,"every":M})
levels = [
    lvl(1,4,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(12,12), s["c"].clone().set_position(7,7)]),
    lvl(2,3,[s["p"].clone().set_position(0,7), s["g"].clone().set_position(13,7), s["c"].clone().set_position(6,6), s["c"].clone().set_position(8,8)]),
    lvl(3,5,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(11,11), s["c"].clone().set_position(5,5)]),
    lvl(4,3,[s["p"].clone().set_position(1,12), s["g"].clone().set_position(12,1), s["c"].clone().set_position(7,6)]),
    lvl(5,4,[s["p"].clone().set_position(3,3), s["g"].clone().set_position(10,10), s["c"].clone().set_position(6,7), s["c"].clone().set_position(7,8)]),
]
class Gc01(ARCBaseGame):
    def __init__(self):
        super().__init__("gc01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._M = int(level.get_data("every") or 4)
        self._t = 0
    def _spread(self):
        add = []
        for sp in list(self.current_level.get_sprites_by_tag("coral")):
            for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                nx, ny = sp.x+dx, sp.y+dy
                gw, gh = self.current_level.grid_size
                if 0<=nx<gw and 0<=ny<gh:
                    h = self.current_level.get_sprite_at(nx,ny,ignore_collidable=True)
                    if not h:
                        add.append((nx,ny))
        for nx, ny in add:
            self.current_level.add_sprite(spr()["c"].clone().set_position(nx,ny))
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
        self._t += 1
        if self._t % self._M == 0:
            self._spread()
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
