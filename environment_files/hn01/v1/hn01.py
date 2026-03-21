"""Plan #15: three-peg Hanoi with three disks."""
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
