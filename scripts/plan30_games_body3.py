# Part 3 — hn01 fb01 lp01 rb01 at01 wb01 lk01
ALL: list[tuple] = []


def _add(stem, title, desc, tags, grid, actions, py):
    ALL.append((stem, title, desc, tags, grid, actions, py))


_add(
    "hn01",
    "Tower of Hanoi",
    "ACTION1–3 select peg A/B/C; ACTION5 picks or drops top disk (no big-on-small). Stack on right peg to win.",
    ["static", "logic"],
    [10, 12],
    5,
    r'''"""Plan #15: three-peg Hanoi with three disks."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
PEGX = (2, 5, 8)
BASEY = 9
def spr():
    return {"d1": Sprite(pixels=[[11]], name="d1", visible=True, collidable=False, tags=["disk","1"]),
            "d2": Sprite(pixels=[[12]], name="d2", visible=True, collidable=False, tags=["disk","2"]),
            "d3": Sprite(pixels=[[13]], name="d3", visible=True, collidable=False, tags=["disk","3"]),
            "peg": Sprite(pixels=[[3]], name="peg", visible=True, collidable=True, tags=["peg"])}
s = spr()
def lvl(d):
    parts = [s["peg"].clone().set_position(x, BASEY) for x in PEGX]
    parts += [s["d3"].clone().set_position(2, BASEY-1), s["d2"].clone().set_position(2, BASEY-2), s["d1"].clone().set_position(2, BASEY-3)]
    return Level(sprites=parts, grid_size=(10,12), data={"difficulty":d})
levels = [lvl(i) for i in range(1,6)]
class Hn01(ARCBaseGame):
    def __init__(self):
        super().__init__("hn01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,5])
    def on_set_level(self, level: Level):
        self._st = [[3,2,1], [], []]
        self._hand = None
        self._peg = 0
        self._ds = {1: None, 2: None, 3: None}
        for sp in self.current_level._sprites:
            if "disk" not in sp.tags:
                continue
            for t in sp.tags:
                if t.isdigit():
                    self._ds[int(t)] = sp
        self._layout()
    def _layout(self):
        for pi, stack in enumerate(self._st):
            x = PEGX[pi]
            for i, sz in enumerate(stack):
                sp = self._ds[sz]
                if sp is not None:
                    sp.set_position(x, BASEY - 1 - i)
        if self._hand:
            sp = self._ds[self._hand]
            if sp is not None:
                sp.set_position(PEGX[self._peg], 2)
    def step(self):
        v = self.action.id.value
        if v in (1,2,3):
            self._peg = v - 1
        elif self.action.id == GameAction.ACTION5:
            st = self._st[self._peg]
            if self._hand is None and st:
                self._hand = st.pop()
            elif self._hand is not None:
                top = st[-1] if st else 99
                if top > self._hand:
                    st.append(self._hand)
                    self._hand = None
        self._layout()
        if self._st[2] == [3,2,1]:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "fb01",
    "Fuse Bomb",
    "Push orange bombs; fuse counts down each step; at 0 removes weak walls in radius 1 and loses if you are in the blast.",
    ["static", "hazard"],
    [12, 12],
    4,
    r'''"""Plan #17: pushable ticking bombs."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "b": Sprite(pixels=[[8]], name="b", visible=True, collidable=True, tags=["bomb"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"]),
            "weak": Sprite(pixels=[[2]], name="weak", visible=True, collidable=True, tags=["weak"])}
s = spr()
def lvl(d, parts):
    return Level(sprites=parts, grid_size=(12,12), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(1,6), s["g"].clone().set_position(10,6), s["b"].clone().set_position(4,6), s["weak"].clone().set_position(7,6)]),
    lvl(2,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(10,10), s["b"].clone().set_position(5,5), s["weak"].clone().set_position(8,5), s["weak"].clone().set_position(8,6)]),
    lvl(3,[s["p"].clone().set_position(2,6), s["g"].clone().set_position(10,6), s["b"].clone().set_position(5,6), s["weak"].clone().set_position(8,4), s["weak"].clone().set_position(8,8)]),
    lvl(4,[s["p"].clone().set_position(0,0), s["g"].clone().set_position(11,11), s["b"].clone().set_position(3,3), s["weak"].clone().set_position(6,6)]),
    lvl(5,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(10,5), s["b"].clone().set_position(5,5), s["weak"].clone().set_position(9,5)]),
]
class Fb01(ARCBaseGame):
    def __init__(self):
        super().__init__("fb01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._fuse = {id(b): 5 for b in self.current_level.get_sprites_by_tag("bomb")}
    def _tick(self):
        dead = []
        for b in self.current_level.get_sprites_by_tag("bomb"):
            k = id(b)
            self._fuse[k] = self._fuse.get(k, 5) - 1
            if self._fuse[k] <= 0:
                dead.append(b)
        for b in dead:
            bx, by = b.x, b.y
            self.current_level.remove_sprite(b)
            if id(b) in self._fuse:
                del self._fuse[id(b)]
            for sp in list(self.current_level._sprites):
                if "weak" in sp.tags and abs(sp.x - bx) + abs(sp.y - by) <= 1:
                    self.current_level.remove_sprite(sp)
            if abs(self._p.x - bx) + abs(self._p.y - by) <= 1:
                self.lose()
                return True
        return False
    def step(self):
        dx = dy = 0
        v = self.action.id.value
        if v == 1:
            dy = -1
        elif v == 2:
            dy = 1
        elif v == 3:
            dx = -1
        elif v == 4:
            dx = 1
        else:
            self.complete_action()
            return
        gw, gh = self.current_level.grid_size
        nx, ny = self._p.x + dx, self._p.y + dy
        if 0 <= nx < gw and 0 <= ny < gh:
            h = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
            if h and "bomb" in h.tags:
                bx, by = nx + dx, ny + dy
                if 0 <= bx < gw and 0 <= by < gh:
                    bh = self.current_level.get_sprite_at(bx, by, ignore_collidable=True)
                    if bh and bh.is_collidable and "weak" not in bh.tags:
                        self.complete_action()
                        return
                    if bh and "weak" in bh.tags:
                        self.current_level.remove_sprite(bh)
                    h.set_position(bx, by)
                    self._p.set_position(nx, ny)
            elif not h or not h.is_collidable:
                self._p.set_position(nx, ny)
        if self._tick():
            self.complete_action()
            return
        if self._p.x == self._g.x and self._p.y == self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "lp01",
    "Letter Path",
    "Visit letter pads in authored order (A→B→C…); wrong letter loses.",
    ["static", "order"],
    [9, 11],
    4,
    r'''"""Plan #19: ordered letter tiles."""
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
''',
)

_add(
    "rb01",
    "Rhythm Gate",
    "Movement only applies on beat (every B world steps); other actions are no-ops.",
    ["static", "timing"],
    [11, 11],
    4,
    r'''"""Plan #20: beat-gated moves."""
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
''',
)

_add(
    "at01",
    "Ant Trail",
    "ACTION5 drops pheromone; ant steps toward strongest adjacent scent each turn; guide it to the green hole.",
    ["static", "simulation"],
    [16, 16],
    5,
    r'''"""Plan #21: pheromone + one ant."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "a": Sprite(pixels=[[6]], name="a", visible=True, collidable=False, tags=["ant"]),
            "h": Sprite(pixels=[[14]], name="h", visible=True, collidable=False, tags=["hole"]),
            "z": Sprite(pixels=[[8]], name="z", visible=True, collidable=True, tags=["hazard"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(16,16), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(1,1), s["a"].clone().set_position(3,3), s["h"].clone().set_position(14,14)]),
    lvl(2,[s["p"].clone().set_position(2,2), s["a"].clone().set_position(4,4), s["h"].clone().set_position(12,12), s["z"].clone().set_position(8,8)]),
    lvl(3,[s["p"].clone().set_position(0,8), s["a"].clone().set_position(2,8), s["h"].clone().set_position(15,8)]),
    lvl(4,[s["p"].clone().set_position(1,1), s["a"].clone().set_position(5,5), s["h"].clone().set_position(10,10)]),
    lvl(5,[s["p"].clone().set_position(3,3), s["a"].clone().set_position(6,6), s["h"].clone().set_position(13,13), s["z"].clone().set_position(9,9)]),
]
class At01(ARCBaseGame):
    def __init__(self):
        super().__init__("at01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4,5])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._ant = self.current_level.get_sprites_by_tag("ant")[0]
        self._hole = self.current_level.get_sprites_by_tag("hole")[0]
        gw, gh = level.grid_size
        self._ph = [[0]*gw for _ in range(gh)]
    def step(self):
        if self.action.id == GameAction.ACTION5:
            self._ph[self._p.y][self._p.x] += 5
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
                self._p.set_position(nx,ny)
        for y in range(gh):
            for x in range(gw):
                self._ph[y][x] = max(0, int(self._ph[y][x] * 0.9))
        ax, ay = self._ant.x, self._ant.y
        best, bx, by = -1, ax, ay
        for ddx, ddy in ((0,1),(0,-1),(1,0),(-1,0)):
            tx, ty = ax+ddx, ay+ddy
            if 0<=tx<gw and 0<=ty<gh:
                hit = self.current_level.get_sprite_at(tx,ty,ignore_collidable=True)
                if hit and hit.is_collidable and "hazard" in hit.tags:
                    continue
                sc = self._ph[ty][tx]
                if sc > best:
                    best, bx, by = sc, tx, ty
        self._ant.set_position(bx,by)
        ah = self.current_level.get_sprite_at(bx,by,ignore_collidable=True)
        if ah and "hazard" in ah.tags:
            self.lose(); self.complete_action(); return
        if bx==self._hole.x and by==self._hole.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "wb01",
    "Wall Belt",
    "One row of wall segments shifts east each step (wrap); reach the goal.",
    ["static", "timing"],
    [16, 16],
    4,
    r'''"""Plan #22: conveyor row of walls."""
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
''',
)

_add(
    "lk01",
    "Lock Tumblers",
    "ACTION1–3 cycle tumblers 0–5; when all match targets the door (gray wall) opens; reach goal.",
    ["static", "logic"],
    [10, 10],
    5,
    r'''"""Plan #23: tumbler combo."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "d": Sprite(pixels=[[3]], name="d", visible=True, collidable=True, tags=["door"])}
s = spr()
def lvl(d, t0, t1, t2):
    return Level(sprites=[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5), s["d"].clone().set_position(5,5)],
                 grid_size=(10,10), data={"difficulty":d,"target":[t0,t1,t2]})
levels = [lvl(1,2,3,1), lvl(2,1,1,4), lvl(3,0,5,2), lvl(4,3,3,3), lvl(5,4,2,0)]
class Lk01(ARCBaseGame):
    def __init__(self):
        super().__init__("lk01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        ds = self.current_level.get_sprites_by_tag("door")
        self._door = ds[0] if ds else None
        self._t = [0, 0, 0]
        self._tar = list(level.get_data("target"))
    def step(self):
        v = self.action.id.value
        if self._door is not None:
            if v == 1:
                self._t[0] = (self._t[0] + 1) % 6
            elif v == 2:
                self._t[1] = (self._t[1] + 1) % 6
            elif v == 3:
                self._t[2] = (self._t[2] + 1) % 6
            if self._t == self._tar and self._door in self.current_level._sprites:
                self.current_level.remove_sprite(self._door)
                self._door = None
        else:
            dx = dy = 0
            if v == 1:
                dy = -1
            elif v == 2:
                dy = 1
            elif v == 3:
                dx = -1
            elif v == 4:
                dx = 1
            gw, gh = self.current_level.grid_size
            nx, ny = self._p.x + dx, self._p.y + dy
            if 0 <= nx < gw and 0 <= ny < gh:
                hit = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
                if not hit or not hit.is_collidable:
                    self._p.set_position(nx, ny)
        if self._p.x == self._g.x and self._p.y == self._g.y:
            self.next_level()
        self.complete_action()
''',
)
