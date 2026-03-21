# Part 4 — dn01 qt01 vt01 fc01 pj01 gc01 sr01
ALL: list[tuple] = []


def _add(stem, title, desc, tags, grid, actions, py):
    ALL.append((stem, title, desc, tags, grid, actions, py))


_add(
    "dn01",
    "Donut Wind",
    "Torus wrap on a 16×16 grid; crossing the east seam increments winding — need ≥2 winding to clear the goal.",
    ["static", "topology"],
    [16, 16],
    4,
    r'''"""Plan #24: torus + winding counter."""
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
''',
)

_add(
    "qt01",
    "Quantum Split",
    "Step on magenta splitter; until cyan observe, moves apply to two ghost positions; observer collapses to the real one.",
    ["static", "logic"],
    [10, 10],
    4,
    r'''"""Plan #25: split/merge ghost positions."""
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
''',
)

_add(
    "vt01",
    "Vote Plates",
    "Gray plate sums crate weights (1/2/4 tags); opens when sum mod M matches target; then reach goal.",
    ["static", "logic"],
    [12, 12],
    4,
    r'''"""Plan #26: weighted crates mod M."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "plate": Sprite(pixels=[[2]], name="plate", visible=True, collidable=False, tags=["plate"]),
            "b1": Sprite(pixels=[[11]], name="b1", visible=True, collidable=True, tags=["block","w1"]),
            "b2": Sprite(pixels=[[12]], name="b2", visible=True, collidable=True, tags=["block","w2"]),
            "b4": Sprite(pixels=[[13]], name="b4", visible=True, collidable=True, tags=["block","w4"]),
            "door": Sprite(pixels=[[3]], name="door", visible=True, collidable=True, tags=["door"])}
s = spr()
def lvl(d, M, tgt, parts):
    return Level(sprites=parts, grid_size=(12,12), data={"difficulty":d,"M":M,"target":tgt})
levels = [
    lvl(1,7,3,[s["p"].clone().set_position(1,6), s["g"].clone().set_position(10,6), s["plate"].clone().set_position(5,6),
              s["b1"].clone().set_position(4,6), s["b2"].clone().set_position(6,6), s["door"].clone().set_position(8,6)]),
    lvl(2,5,0,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(9,9), s["plate"].clone().set_position(5,5),
              s["b4"].clone().set_position(4,5), s["door"].clone().set_position(7,7)]),
    lvl(3,6,2,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(10,10), s["plate"].clone().set_position(6,6),
              s["b1"].clone().set_position(5,6), s["b2"].clone().set_position(7,6), s["door"].clone().set_position(9,5)]),
    lvl(4,8,4,[s["p"].clone().set_position(0,6), s["g"].clone().set_position(11,6), s["plate"].clone().set_position(4,6),
              s["b2"].clone().set_position(3,6), s["b2"].clone().set_position(5,6), s["door"].clone().set_position(9,6)]),
    lvl(5,7,1,[s["p"].clone().set_position(2,5), s["g"].clone().set_position(9,5), s["plate"].clone().set_position(5,5),
              s["b1"].clone().set_position(4,5), s["b4"].clone().set_position(6,5), s["door"].clone().set_position(8,5)]),
]
class Vt01(ARCBaseGame):
    def __init__(self):
        super().__init__("vt01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._M = int(level.get_data("M"))
        self._tgt = int(level.get_data("target"))
        self._plates = {(sp.x,sp.y) for sp in self.current_level.get_sprites_by_tag("plate")}
        ds = self.current_level.get_sprites_by_tag("door")
        self._door = ds[0] if ds else None
    def _sum_mod(self):
        s = 0
        for sp in self.current_level.get_sprites_by_tag("block"):
            if (sp.x, sp.y) not in self._plates:
                continue
            if "w1" in sp.tags:
                s += 1
            elif "w2" in sp.tags:
                s += 2
            elif "w4" in sp.tags:
                s += 4
        return s % self._M
    def _on_plate(self):
        return (self._p.x, self._p.y) in self._plates
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
            if h and "block" in h.tags:
                bx, by = nx+dx, ny+dy
                if 0<=bx<gw and 0<=by<gh:
                    bh = self.current_level.get_sprite_at(bx,by,ignore_collidable=True)
                    if not bh or not bh.is_collidable:
                        h.set_position(bx,by)
                        self._p.set_position(nx,ny)
            elif not h or not h.is_collidable:
                self._p.set_position(nx,ny)
        if self._sum_mod() == self._tgt and self._door and self._door in self.current_level._sprites:
            self.current_level.remove_sprite(self._door)
            self._door = None
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "fc01",
    "Follow Chain",
    "Three tail sprites copy your previous positions each step; avoid overlapping them; all must reach the exit zone.",
    ["static", "coordination"],
    [14, 10],
    4,
    r'''"""Plan #27: follow-the-leader chain."""
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
''',
)

_add(
    "pj01",
    "Bolt Bounce",
    "A red bolt moves east each step; ACTION6 toggles a mirror on an empty cell (/ vs \\); guide the bolt into the yellow sink without hitting you.",
    ["static", "timing"],
    [14, 14],
    6,
    r'''"""Plan #28: stepping bolt + mirrors."""
from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "b": Sprite(pixels=[[8]], name="b", visible=True, collidable=False, tags=["bolt"]),
            "k": Sprite(pixels=[[11]], name="k", visible=True, collidable=False, tags=["sink"]),
            "m": Sprite(pixels=[[7]], name="m", visible=True, collidable=False, tags=["mirror","fs"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(14,14), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(0,7), s["b"].clone().set_position(2,7), s["k"].clone().set_position(12,7)]),
    lvl(2,[s["p"].clone().set_position(0,3), s["b"].clone().set_position(1,7), s["k"].clone().set_position(12,3)]),
    lvl(3,[s["p"].clone().set_position(1,1), s["b"].clone().set_position(2,10), s["k"].clone().set_position(10,2)]),
    lvl(4,[s["p"].clone().set_position(2,2), s["b"].clone().set_position(3,7), s["k"].clone().set_position(11,11)]),
    lvl(5,[s["p"].clone().set_position(0,0), s["b"].clone().set_position(2,5), s["k"].clone().set_position(13,13)]),
]
class Pj01(ARCBaseGame):
    def __init__(self):
        super().__init__("pj01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4,6])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._bolt = self.current_level.get_sprites_by_tag("bolt")[0]
        self._sink = self.current_level.get_sprites_by_tag("sink")[0]
        self._bdx, self._bdy = 1, 0
    def step(self):
        if self.action.id == GameAction.ACTION6:
            px, py = int(self.action.data.get("x",0)), int(self.action.data.get("y",0))
            h = self.camera.display_to_grid(px, py)
            if h:
                gx, gy = int(h[0]), int(h[1])
                cell = self.current_level.get_sprite_at(gx,gy,ignore_collidable=True)
                if not cell:
                    self.current_level.add_sprite(spr()["m"].clone().set_position(gx,gy))
                elif "mirror" in cell.tags:
                    if "fs" in cell.tags:
                        cell.tags.remove("fs")
                        cell.tags.append("bs")
                    else:
                        cell.tags.remove("bs")
                        cell.tags.append("fs")
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
        bx, by = self._bolt.x + self._bdx, self._bolt.y + self._bdy
        if not (0 <= bx < gw and 0 <= by < gh):
            self.complete_action()
            return
        mh = self.current_level.get_sprite_at(bx, by, ignore_collidable=True)
        if mh and "mirror" in mh.tags:
            if "fs" in mh.tags:
                self._bdx, self._bdy = -self._bdy, -self._bdx
            else:
                self._bdx, self._bdy = self._bdy, self._bdx
        self._bolt.set_position(bx, by)
        if self._bolt.x==self._p.x and self._bolt.y==self._p.y:
            self.lose(); self.complete_action(); return
        if self._bolt.x==self._sink.x and self._bolt.y==self._sink.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "gc01",
    "Coral Creep",
    "Inert coral spreads to empty orth neighbors every M steps; coral blocks movement; reach the goal before you are boxed in.",
    ["static", "growth"],
    [14, 14],
    4,
    r'''"""Plan #29: non-lethal spreading coral."""
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
''',
)

_add(
    "sr01",
    "Aura Algebra",
    "Stepping colored zones toggles RGB bits of your aura; the exit unlocks only when aura matches (xor) the target triple.",
    ["static", "logic"],
    [12, 12],
    4,
    r'''"""Plan #30: RGB aura + XOR door."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "dr": Sprite(pixels=[[8]], name="dr", visible=True, collidable=False, tags=["zone","r"]),
            "dg": Sprite(pixels=[[14]], name="dg", visible=True, collidable=False, tags=["zone","gn"]),
            "db": Sprite(pixels=[[10]], name="db", visible=True, collidable=False, tags=["zone","b"]),
            "wash": Sprite(pixels=[[1]], name="wash", visible=True, collidable=False, tags=["wash"]),
            "door": Sprite(pixels=[[3]], name="door", visible=True, collidable=True, tags=["door"])}
s = spr()
def lvl(d, parts, tr, tg, tb):
    return Level(sprites=parts, grid_size=(12,12), data={"difficulty":d,"tr":tr,"tg":tg,"tb":tb})
levels = [
    lvl(1,[s["p"].clone().set_position(1,6), s["g"].clone().set_position(10,6), s["dr"].clone().set_position(3,6), s["dg"].clone().set_position(5,6), s["door"].clone().set_position(8,6)], 1,1,0),
    lvl(2,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(9,9), s["db"].clone().set_position(4,4), s["wash"].clone().set_position(6,6), s["door"].clone().set_position(7,7)], 0,0,1),
    lvl(3,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(10,10), s["dr"].clone().set_position(3,3), s["dg"].clone().set_position(4,4), s["db"].clone().set_position(5,5), s["door"].clone().set_position(8,8)], 1,0,1),
    lvl(4,[s["p"].clone().set_position(0,6), s["g"].clone().set_position(11,6), s["wash"].clone().set_position(2,6), s["dr"].clone().set_position(5,6), s["door"].clone().set_position(9,6)], 1,0,0),
    lvl(5,[s["p"].clone().set_position(2,5), s["g"].clone().set_position(9,5), s["dg"].clone().set_position(4,5), s["db"].clone().set_position(6,5), s["door"].clone().set_position(8,5)], 0,1,1),
]
class Sr01(ARCBaseGame):
    def __init__(self):
        super().__init__("sr01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._ar, self._ag, self._ab = 0, 0, 0
        self._tr = int(level.get_data("tr"))
        self._tg = int(level.get_data("tg"))
        self._tb = int(level.get_data("tb"))
        ds = self.current_level.get_sprites_by_tag("door")
        self._door = ds[0] if ds else None
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
        hit = self.current_level.get_sprite_at(self._p.x,self._p.y,ignore_collidable=True)
        if hit and "wash" in hit.tags:
            self._ar, self._ag, self._ab = 0, 0, 0
        elif hit and "zone" in hit.tags:
            if "r" in hit.tags:
                self._ar ^= 1
            if "gn" in hit.tags:
                self._ag ^= 1
            if "b" in hit.tags:
                self._ab ^= 1
        if ((self._ar ^ self._tr) | (self._ag ^ self._tg) | (self._ab ^ self._tb)) == 0 and self._door and self._door in self.current_level._sprites:
            self.current_level.remove_sprite(self._door)
            self._door = None
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)
