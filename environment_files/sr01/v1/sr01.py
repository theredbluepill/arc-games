"""Plan #30: RGB aura + XOR door."""
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
