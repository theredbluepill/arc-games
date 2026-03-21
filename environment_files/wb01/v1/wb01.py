"""Plan #22: conveyor row of walls."""
from arcengine import ARCBaseGame, GameState, Camera, Level, RenderableUserDisplay, Sprite
BG, PAD = 5, 4
def _rp(frame, h, w, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        frame[y, x] = c


def _r_dots(frame, h, w, li, n, y0=0):
    for i in range(min(n, 14)):
        cx = 1 + i * 2
        if cx >= w:
            break
        c = 14 if i < li else (11 if i == li else 3)
        _rp(frame, h, w, cx, y0, c)


def _r_bar(frame, h, w, game_over, win):
    if not (game_over or win):
        return
    r = h - 3
    if r < 0:
        return
    c = 14 if win else 8
    for x in range(min(w, 16)):
        _rp(frame, h, w, x, r, c)


class U(RenderableUserDisplay):
    def __init__(self, num_levels: int) -> None:
        self._num_levels = num_levels
        self._level_index = 0
        self._state = None

    def update(self, *, level_index: int | None = None, state=None) -> None:
        if level_index is not None:
            self._level_index = level_index
        if state is not None:
            self._state = state

    def render_interface(self, f):
        import numpy as np

        from arcengine import GameState

        if not isinstance(f, np.ndarray):
            return f
        h, w = f.shape
        _r_dots(f, h, w, self._level_index, self._num_levels, 0)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(f, h, w, go, win)
        return f

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
        self._ui = U(len(levels))
        super().__init__("wb01", levels, Camera(0,0,16,16,BG,PAD,[self._ui]), False, 1, [1,2,3,4])
    def on_set_level(self, level: Level):
        self._p = self.current_level.get_sprites_by_tag("player")[0]
        self._ui.update(level_index=self.level_index, state=self._state)

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
            self._ui.update(level_index=self.level_index, state=self._state)
            self.lose(); self.complete_action(); return
        if self._p.x==self._g.x and self._p.y==self._g.y:
            self.next_level()
        self._ui.update(level_index=self.level_index, state=self._state)
        self.complete_action()
