from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Dc01UI(RenderableUserDisplay):
    def __init__(
        self, agent_a_done: bool, agent_b_done: bool, steps: int, limit: int
    ) -> None:
        self._a_done = agent_a_done
        self._b_done = agent_b_done
        self._steps = steps
        self._limit = limit

    def update(self, a_done: bool, b_done: bool, steps: int, limit: int) -> None:
        self._a_done = a_done
        self._b_done = b_done
        self._steps = steps
        self._limit = limit

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        color = 14 if self._a_done else 8
        frame[0, 0] = color
        color = 14 if self._b_done else 8
        frame[0, w - 1] = color
        return frame


sprites = {
    "agent_a": Sprite(
        pixels=[[9]],
        name="agent_a",
        visible=True,
        collidable=True,
        tags=["agent_a", "player"],
        layer=1,
    ),
    "agent_b": Sprite(
        pixels=[[14]],
        name="agent_b",
        visible=True,
        collidable=True,
        tags=["agent_b", "player"],
        layer=1,
    ),
    "goal_a": Sprite(
        pixels=[[10]],
        name="goal_a",
        visible=True,
        collidable=False,
        tags=["goal_a", "goal"],
        layer=0,
    ),
    "goal_b": Sprite(
        pixels=[[12]],
        name="goal_b",
        visible=True,
        collidable=False,
        tags=["goal_b", "goal"],
        layer=0,
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
        layer=2,
    ),
    "hazard": Sprite(
        pixels=[[8]],
        name="hazard",
        visible=True,
        collidable=True,
        tags=["hazard"],
        layer=2,
    ),
}


def make_level(
    grid_width,
    grid_height,
    agent_a_pos,
    agent_b_pos,
    goal_a_pos,
    goal_b_pos,
    left_walls,
    right_walls,
    center_walls,
    hazards,
    step_limit,
):
    sprite_list = [
        sprites["agent_a"].clone().set_position(*agent_a_pos),
        sprites["agent_b"].clone().set_position(*agent_b_pos),
        sprites["goal_a"].clone().set_position(*goal_a_pos),
        sprites["goal_b"].clone().set_position(*goal_b_pos),
    ]
    for w in left_walls:
        sprite_list.append(sprites["wall"].clone().set_position(*w))
    for w in right_walls:
        sprite_list.append(sprites["wall"].clone().set_position(*w))
    for w in center_walls:
        sprite_list.append(sprites["wall"].clone().set_position(*w))
    for h in hazards:
        sprite_list.append(sprites["hazard"].clone().set_position(*h))
    return Level(
        sprites=sprite_list,
        grid_size=(grid_width, grid_height),
        data={"step_limit": step_limit},
    )


levels = [
    make_level(
        16,
        8,
        agent_a_pos=(0, 3),
        agent_b_pos=(15, 3),
        goal_a_pos=(7, 3),
        goal_b_pos=(9, 3),
        left_walls=[],
        right_walls=[],
        center_walls=[(10, 0), (10, 1), (10, 2), (10, 4), (10, 5), (10, 6), (10, 7)],
        hazards=[],
        step_limit=30,
    ),
    make_level(
        18,
        10,
        agent_a_pos=(0, 4),
        agent_b_pos=(17, 4),
        goal_a_pos=(8, 4),
        goal_b_pos=(10, 4),
        left_walls=[(3, 3), (3, 5), (6, 2), (6, 6)],
        right_walls=[(13, 2), (13, 3), (13, 5), (13, 6), (13, 1), (13, 7)],
        center_walls=[
            (9, 0),
            (9, 1),
            (9, 3),
            (9, 4),
            (9, 5),
            (9, 6),
            (9, 7),
            (9, 8),
            (9, 9),
        ],
        hazards=[],
        step_limit=40,
    ),
    make_level(
        20,
        10,
        agent_a_pos=(0, 4),
        agent_b_pos=(19, 4),
        goal_a_pos=(8, 4),
        goal_b_pos=(11, 4),
        left_walls=[(3, 2), (3, 6), (6, 2), (6, 6)],
        right_walls=[(13, 2), (13, 6), (16, 2), (16, 6)],
        center_walls=[
            (10, 0),
            (10, 1),
            (10, 3),
            (10, 5),
            (10, 6),
            (10, 7),
            (10, 8),
            (10, 9),
        ],
        hazards=[],
        step_limit=50,
    ),
    make_level(
        22,
        12,
        agent_a_pos=(0, 5),
        agent_b_pos=(21, 5),
        goal_a_pos=(9, 5),
        goal_b_pos=(12, 5),
        left_walls=[(3, 3), (3, 7), (6, 3), (6, 7), (9, 3), (9, 7)],
        right_walls=[(13, 3), (13, 7), (16, 3), (16, 7), (19, 3), (19, 7)],
        center_walls=[
            (11, 0),
            (11, 1),
            (11, 2),
            (11, 4),
            (11, 6),
            (11, 8),
            (11, 9),
            (11, 10),
            (11, 11),
        ],
        hazards=[],
        step_limit=60,
    ),
    make_level(
        24,
        12,
        agent_a_pos=(0, 5),
        agent_b_pos=(23, 5),
        goal_a_pos=(10, 5),
        goal_b_pos=(13, 5),
        left_walls=[(3, 3), (3, 7), (6, 3), (6, 7), (9, 3), (9, 7)],
        right_walls=[(14, 3), (14, 7), (17, 3), (17, 7), (20, 3), (20, 7)],
        center_walls=[
            (12, 0),
            (12, 1),
            (12, 2),
            (12, 4),
            (12, 6),
            (12, 8),
            (12, 9),
            (12, 10),
            (12, 11),
        ],
        hazards=[
            (4, 5),
            (6, 5),
            (8, 5),
            (15, 5),
            (17, 5),
            (19, 5),
        ],
        step_limit=80,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Dc01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Dc01UI(False, False, 0, 0)
        super().__init__(
            "dc01",
            levels,
            Camera(0, 0, 24, 12, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5, 6, 7],
        )

    def on_set_level(self, level: Level) -> None:
        self._agent_a = self.current_level.get_sprites_by_tag("agent_a")[0]
        self._agent_b = self.current_level.get_sprites_by_tag("agent_b")[0]
        self._goal_a = self.current_level.get_sprites_by_tag("goal_a")[0]
        self._goal_b = self.current_level.get_sprites_by_tag("goal_b")[0]
        self._steps = 0
        self._step_limit = self.current_level.get_data("step_limit")
        self._a_done = False
        self._b_done = False
        self._ui.update(self._a_done, self._b_done, self._steps, self._step_limit)

    def step(self) -> None:
        dx = 0
        dy = 0
        agent = None

        if self.action.id.value == 1:
            dy = -1
            agent = self._agent_a
        elif self.action.id.value == 2:
            dy = 1
            agent = self._agent_a
        elif self.action.id.value == 3:
            dx = -1
            agent = self._agent_a
        elif self.action.id.value == 4:
            dx = 1
            agent = self._agent_a
        elif self.action.id.value == 5:
            dy = -1
            agent = self._agent_b
        elif self.action.id.value == 6:
            dy = 1
            agent = self._agent_b
        elif self.action.id.value == 7:
            dx = -1
            agent = self._agent_b

        if agent is None:
            self.complete_action()
            return

        new_x = agent.x + dx
        new_y = agent.y + dy

        grid_w, grid_h = self.current_level.grid_size
        if not (0 <= new_x < grid_w and 0 <= new_y < grid_h):
            self.complete_action()
            return

        sprite = self.current_level.get_sprite_at(new_x, new_y, ignore_collidable=True)

        if sprite and "hazard" in sprite.tags:
            self.lose()
            self.complete_action()
            return

        if sprite and "wall" in sprite.tags:
            self.complete_action()
            return

        if (
            sprite
            and "goal_a" in sprite.tags
            and agent is self._agent_a
            and not self._a_done
        ):
            self._a_done = True
        elif (
            sprite
            and "goal_b" in sprite.tags
            and agent is self._agent_b
            and not self._b_done
        ):
            self._b_done = True

        agent.set_position(new_x, new_y)

        self._steps += 1
        self._ui.update(self._a_done, self._b_done, self._steps, self._step_limit)

        if self._a_done and self._b_done:
            self.next_level()
        elif self._steps >= self._step_limit:
            self.lose()

        self.complete_action()
