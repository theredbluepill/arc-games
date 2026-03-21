"""Plan #19: ordered letter tiles."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def L(letter, x, y):
    sp = Sprite(pixels=[[10]], name=letter, visible=True, collidable=False, tags=["letter", letter])
    return sp.set_position(x, y)
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d, seq, positions, goal):
    parts = [s["p"].clone().set_position(*positions[0]), s["g"].clone().set_position(*goal)]
    for i, ch in enumerate(seq):
        parts.append(L(ch, positions[i+1][0], positions[i+1][1]).set_position(*positions[i+1]))
    return Level(sprites=parts, grid_size=(9,11), data={"difficulty":d,"seq":list(seq)})
levels = [
    lvl(1, "AB", [(1,5),(3,5),(7,5)], (7,9)),
    lvl(2, "ABC", [(1,1),(2,3),(4,5),(7,8)], (7,9)),
    lvl(3, "AB", [(2,9),(5,5),(8,2)], (8,2)),
    lvl(4, "ABC", [(0,0),(4,4),(6,2),(8,10)], (8,10)),
    lvl(5, "AB", [(3,3),(6,6),(3,9)], (3,9)),
]
class Lp01(ARCBaseGame):
    def __init__(self):
        super().__init__("lp01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._seq = list(level.get_data("seq"))
        self._ni = 0
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
            if h and "letter" in h.tags:
                want = self._seq[self._ni] if self._ni < len(self._seq) else None
                got = [t for t in h.tags if len(t)==1 and t.isalpha()][0]
                if want and got == want:
                    self._ni += 1
                    self.current_level.remove_sprite(h)
                else:
                    self.lose(); self.complete_action(); return
            elif not h or not h.is_collidable:
                self._p.set_position(nx,ny)
        if self._ni >= len(self._seq) and self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
