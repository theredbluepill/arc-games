"""Plan #12: vertical mirror ghost."""
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
