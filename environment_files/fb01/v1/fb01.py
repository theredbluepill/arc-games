"""Plan #17: pushable ticking bombs."""
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
