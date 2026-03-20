# Part 2 — 7 games: sc01 au01 cf01 ep01 tf01 ec01 tk01
ALL: list[tuple] = []


def _add(stem, title, desc, tags, grid, actions, py):
    ALL.append((stem, title, desc, tags, grid, actions, py))


_add(
    "sc01",
    "Scent Stealth",
    "Guards face east; high scent on a tile while in their cone line-of-sight loses. Scent decays when you leave a trail.",
    ["static", "stealth"],
    [14, 14],
    6,
    r'''"""Plan #6: guard cone + scent grid."""
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
''',
)

_add(
    "au01",
    "Bonus Steps",
    "Low step budget; stepping on cyan bonus pads adds steps (auctioned resource feel).",
    ["static", "planning"],
    [10, 10],
    4,
    r'''"""Plan #7: touch bonus pads for +step budget."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self, s, b): self.s, self.b = s, b
    def update(self, s, b): self.s, self.b = s, b
    def render_interface(self, f):
        import numpy as np
        if isinstance(f, np.ndarray):
            h, w = f.shape
            for i in range(min(self.b, 8)): f[h-2,2+i]=11
        return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "b": Sprite(pixels=[[10]], name="b", visible=True, collidable=False, tags=["bonus"])}
s = spr()
def lvl(d, parts, lim, add):
    return Level(sprites=parts, grid_size=(10,10), data={"difficulty":d,"limit":lim,"bonus":add})
levels = [
    lvl(1,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(8,8), s["b"].clone().set_position(4,4)], 25, 20),
    lvl(2,[s["p"].clone().set_position(0,0), s["g"].clone().set_position(9,9), s["b"].clone().set_position(3,3), s["b"].clone().set_position(6,6)], 30, 15),
    lvl(3,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5), s["b"].clone().set_position(5,5)], 22, 25),
    lvl(4,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(7,7), s["b"].clone().set_position(4,5)], 28, 18),
    lvl(5,[s["p"].clone().set_position(0,9), s["g"].clone().set_position(9,0), s["b"].clone().set_position(5,2), s["b"].clone().set_position(5,7)], 35, 12),
]
class Au01(ARCBaseGame):
    def __init__(self):
        self._ui = U(0,0)
        super().__init__("au01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._lim = int(level.get_data("limit"))
        self._bonus = int(level.get_data("bonus"))
        self._steps = 0
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
                if h and "bonus" in h.tags:
                    self.current_level.remove_sprite(h)
                    self._lim += self._bonus
        self._steps += 1
        self._ui.update(self._steps, self._lim)
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        elif self._steps >= self._lim:
            self.lose()
        self.complete_action()
''',
)

_add(
    "cf01",
    "Crop Fallow",
    "Re-entering a cell before F world steps pass loses.",
    ["static", "path"],
    [10, 10],
    4,
    r'''"""Plan #8: fallow timer per cell."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d,parts,F):
    return Level(sprites=parts, grid_size=(10,10), data={"difficulty":d,"fallow":F})
levels = [lvl(1,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(8,8)],4),
          lvl(2,[s["p"].clone().set_position(0,0), s["g"].clone().set_position(9,9)],5),
          lvl(3,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(7,7)],3),
          lvl(4,[s["p"].clone().set_position(1,5), s["g"].clone().set_position(8,5)],4),
          lvl(5,[s["p"].clone().set_position(0,9), s["g"].clone().set_position(9,0)],5)]
class Cf01(ARCBaseGame):
    def __init__(self):
        super().__init__("cf01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._F = int(level.get_data("fallow"))
        self._last = {}
        self._t = 0
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
            k = (nx,ny)
            if k in self._last and self._t - self._last[k] < self._F:
                self.lose(); self.complete_action(); return
            self._p.set_position(nx,ny)
            self._last[k] = self._t
        self._t += 1
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "ep01",
    "Pain Budget",
    "Entering a cell costs its visit count; exceed pain budget to lose.",
    ["static", "path"],
    [12, 12],
    4,
    r'''"""Plan #9: visit-count entry cost + global pain budget."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self, pain): self.p = pain
    def update(self, pain): self.p = pain
    def render_interface(self, f):
        import numpy as np
        if isinstance(f, np.ndarray):
            h,w=f.shape
            c = 8 if self.p < 5 else 14
            f[h-2,2]=c
        return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"])}
s = spr()
def lvl(d,parts,budget):
    return Level(sprites=parts, grid_size=(12,12), data={"difficulty":d,"budget":budget})
levels = [lvl(1,[s["p"].clone().set_position(1,1), s["g"].clone().set_position(10,10)],40),
          lvl(2,[s["p"].clone().set_position(0,0), s["g"].clone().set_position(11,11)],35),
          lvl(3,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(9,9)],45),
          lvl(4,[s["p"].clone().set_position(1,6), s["g"].clone().set_position(10,6)],38),
          lvl(5,[s["p"].clone().set_position(5,1), s["g"].clone().set_position(5,10)],42)]
class Ep01(ARCBaseGame):
    def __init__(self):
        self._ui = U(40)
        super().__init__("ep01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._bud = int(level.get_data("budget"))
        self._pain = 0
        self._vc = {}
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
            c = self._vc.get((nx,ny),0)
            self._pain += c
            if self._pain > self._bud:
                self.lose(); self.complete_action(); return
            self._vc[(nx,ny)] = c + 1
            self._p.set_position(nx,ny)
        self._ui.update(self._bud - self._pain)
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "tf01",
    "Traffic Light",
    "Crossing tile (orange) may be entered only on green phase (cycles every 4 steps).",
    ["static", "timing"],
    [14, 14],
    4,
    r'''"""Plan #11: light phase gate."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def __init__(self, ph): self.ph = ph
    def update(self, ph): self.ph = ph
    def render_interface(self, f):
        import numpy as np
        if isinstance(f, np.ndarray):
            h,w=f.shape
            f[h-2,2] = 14 if self.ph % 4 < 2 else 8
        return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "c": Sprite(pixels=[[12]], name="c", visible=True, collidable=False, tags=["crossing"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(14,14), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(1,7), s["g"].clone().set_position(12,7), s["c"].clone().set_position(7,7)]),
    lvl(2,[s["p"].clone().set_position(2,2), s["g"].clone().set_position(11,11), s["c"].clone().set_position(6,6)]),
    lvl(3,[s["p"].clone().set_position(0,7), s["g"].clone().set_position(13,7), s["c"].clone().set_position(8,7)]),
    lvl(4,[s["p"].clone().set_position(3,3), s["g"].clone().set_position(10,10), s["c"].clone().set_position(5,8)]),
    lvl(5,[s["p"].clone().set_position(1,12), s["g"].clone().set_position(12,1), s["c"].clone().set_position(7,6)]),
]
class Tf01(ARCBaseGame):
    def __init__(self):
        self._ui = U(0)
        super().__init__("tf01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._cross = {(s.x,s.y) for s in self.current_level.get_sprites_by_tag("crossing")}
        self._t = 0
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
            if (nx,ny) in self._cross and (self._t % 4) >= 2:
                self.complete_action(); return
            self._p.set_position(nx,ny)
        self._t += 1
        self._ui.update(self._t)
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "ec01",
    "Mirror Echo",
    "A mirror ghost moves with reflected horizontal delta; if the ghost hits a wall your move is blocked.",
    ["static", "planning"],
    [12, 12],
    4,
    r'''"""Plan #12: vertical mirror ghost."""
from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
class U(RenderableUserDisplay):
    def render_interface(self, f): return f
def spr():
    return {"p": Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"]),
            "g": Sprite(pixels=[[14]], name="g", visible=True, collidable=False, tags=["goal"]),
            "w": Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"]),
            "e": Sprite(pixels=[[7]], name="e", visible=True, collidable=False, tags=["echo"])}
s = spr()
def lvl(d,parts):
    return Level(sprites=parts, grid_size=(12,12), data={"difficulty":d})
levels = [
    lvl(1,[s["p"].clone().set_position(2,6), s["e"].clone().set_position(9,6), s["g"].clone().set_position(5,6)]),
    lvl(2,[s["p"].clone().set_position(1,1), s["e"].clone().set_position(10,1), s["g"].clone().set_position(5,10), s["w"].clone().set_position(8,5)]),
    lvl(3,[s["p"].clone().set_position(3,3), s["e"].clone().set_position(8,3), s["g"].clone().set_position(5,9)]),
    lvl(4,[s["p"].clone().set_position(0,6), s["e"].clone().set_position(11,6), s["g"].clone().set_position(6,6)]),
    lvl(5,[s["p"].clone().set_position(2,2), s["e"].clone().set_position(9,2), s["g"].clone().set_position(5,8), s["w"].clone().set_position(4,5), s["w"].clone().set_position(7,5)]),
]
class Ec01(ARCBaseGame):
    def __init__(self):
        super().__init__("ec01", levels, Camera(0,0,16,16,BG,PAD,[U()]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._e = self.current_level.get_sprites_by_tag("echo")[0]
        self._g = self.current_level.get_sprites_by_tag("goal")[0]
        self._mx = 5
    def step(self):
        dx=dy=0
        v=self.action.id.value
        if v==1: dy=-1
        elif v==2: dy=1
        elif v==3: dx=-1
        elif v==4: dx=1
        else: self.complete_action(); return
        gdx = -dx
        gw, gh = self.current_level.grid_size
        enx, eny = self._e.x + gdx, self._e.y + dy
        if not (0 <= enx < gw and 0 <= eny < gh):
            self.complete_action(); return
        eh = self.current_level.get_sprite_at(enx, eny, ignore_collidable=True)
        if eh and eh.is_collidable and "wall" in eh.tags:
            self.complete_action(); return
        nx, ny = self._p.x + dx, self._p.y + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            self.complete_action(); return
        h = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
        if h and h.is_collidable:
            self.complete_action(); return
        self._e.set_position(enx, eny)
        self._p.set_position(nx, ny)
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self.complete_action()
''',
)

_add(
    "tk01",
    "Telekinetic Tug",
    "ACTION5 pulls the nearest crate one Manhattan step toward you if the first hop is clear.",
    ["static", "push"],
    [10, 10],
    5,
    r'''"""Plan #13: ACTION5 tug nearest block."""
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
''',
)
