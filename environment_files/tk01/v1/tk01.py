"""Plan #13: ACTION5 tug nearest block."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "b": Sprite(pixels=[[15]], name="b", visible=True, collidable=True, tags=["block"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(10,10), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5), s["b"].clone().set_position(5,5)]),
    lvl(2,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(8,8), s["b"].clone().set_position(6,4)]),
    lvl(3,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(8,8), s["b"].clone().set_position(4,4), s["w"].clone().set_position(5,4)]),
    lvl(4,[s["p"].clone().set_position(0,5), s["g"].clone().set_position(9,5), s["b"].clone().set_position(7,5)]),
    lvl(5,[s["p"].clone().set_position(3,3), s["g"].clone().set_position(7,7), s["b"].clone().set_position(5,6)]),
]
class Tk01(ARCBaseGame):
    def __init__(self):
        super().__init__("tk01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4,5])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._blocks = self.current_level.get_sprites_by_tag("block")
    def step(self):
        if self.action.id == GameAction.ACTION5:
            best = None
            bd = 999
            for b in self._blocks:
                d = abs(b.x-self._p.x)+abs(b.y-self._p.y)
                if d < bd:
                    bd, best = d, b
            if best and bd > 0:
                dx = (1 if best.x < self._p.x else (-1 if best.x > self._p.x else 0))
                dy = (1 if best.y < self._p.y else (-1 if best.y > self._p.y else 0))
                if dx != 0 and dy != 0:
                    if abs(best.x-self._p.x) > abs(best.y-self._p.y): dy = 0
                    else: dx = 0
                nx, ny = best.x+dx, best.y+dy
                gw, gh = self.current_level.grid_size
                if 0<=nx<gw and 0<=ny<gh:
                    h = self.current_level.get_sprite_at(nx,ny,ignore_collidable=True)
                    if not h or (not h.is_collidable) or h is best:
                        best.set_position(nx,ny)
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
            if h and "block" in h.tags:
                bx, by = nx+dx, ny+dy
                if 0<=bx<gw and 0<=by<gh:
                    bh = self.current_level.get_sprite_at(bx,by,ignore_collidable=True)
                    if not bh or not bh.is_collidable:
                        h.set_position(bx,by)
                        self._p.set_position(nx,ny)
            elif not h or not h.is_collidable:
                self._p.set_position(nx,ny)
        if any(b.x == self._g.x and b.y == self._g.y for b in self._blocks):
            self.next_level()
        self.complete_action()
