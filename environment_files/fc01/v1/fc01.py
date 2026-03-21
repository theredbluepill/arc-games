"""Plan #27: follow-the-leader chain."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "t": Sprite(pixels=[[6]], name="t", visible=True, collidable=True, tags=["tail"]),
            "e": Sprite(pixels=[[14]], name="e", visible=True, collidable=False, tags=["exit"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(14,10), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(2,5), s["t"].clone().set_position(1,5), s["t"].clone().set_position(0,5), s["t"].clone().set_position(0,4), s["e"].clone().set_position(12,5)]),
    lvl(2,[s["p"].clone().set_position(1,1), s["t"].clone().set_position(0,1), s["t"].clone().set_position(0,0), s["t"].clone().set_position(1,0), s["e"].clone().set_position(12,8)]),
    lvl(3,[s["p"].clone().set_position(3,5), s["t"].clone().set_position(2,5), s["t"].clone().set_position(1,5), s["t"].clone().set_position(0,5), s["e"].clone().set_position(11,5)]),
    lvl(4,[s["p"].clone().set_position(2,3), s["t"].clone().set_position(1,3), s["t"].clone().set_position(1,2), s["t"].clone().set_position(1,1), s["e"].clone().set_position(10,7)]),
    lvl(5,[s["p"].clone().set_position(1,5), s["t"].clone().set_position(0,5), s["t"].clone().set_position(0,4), s["t"].clone().set_position(0,3), s["e"].clone().set_position(12,5)]),
]
class Fc01(ARCBaseGame):
    def __init__(self):
        super().__init__("fc01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._tails = self.current_level.get_sprites_by_tag("tail")
        self._ex = self.current_level.get_sprites_by_tag("exit")[0]
    def step(self):
        dx=dy=0
        v=self.action.id.value
        if v==1: dy=-1
        elif v==2: dy=1
        elif v==3: dx=-1
        elif v==4: dx=1
        else: self.complete_action(); return
        px, py = self._p.x, self._p.y
        gw, gh = self.current_level.grid_size
        nx, ny = px+dx, py+dy
        if 0<=nx<gw and 0<=ny<gh:
            h = self.current_level.get_sprite_at(nx,ny,ignore_collidable=True)
            if not h or not h.is_collidable or "tail" in h.tags:
                if h and "tail" in h.tags:
                    self.lose(); self.complete_action(); return
                prev = [(px,py)] + [(t.x,t.y) for t in self._tails]
                self._p.set_position(nx,ny)
                for i, t in enumerate(self._tails):
                    t.set_position(prev[i][0], prev[i][1])
        def near(t):
            return max(abs(t.x - self._ex.x), abs(t.y - self._ex.y)) <= 1

        ok_p = self._p.x == self._ex.x and self._p.y == self._ex.y
        if ok_p and all(near(t) for t in self._tails):
            self.next_level()
        self.complete_action()
