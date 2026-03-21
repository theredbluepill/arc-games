"""Plan #21: pheromone + one ant."""
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
