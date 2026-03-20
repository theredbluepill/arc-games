"""Plan #26: weighted crates mod M."""
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
