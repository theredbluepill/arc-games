from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)
import random


class Wm01UI(RenderableUserDisplay):
    def __init__(
        self, lives: int, score: int, checkpoint_score: int, checkpoint_total: int
    ) -> None:
        self._lives = lives
        self._score = score
        self._checkpoint_score = checkpoint_score
        self._checkpoint_total = checkpoint_total
        self._click_pos = None
        self._click_frames = 0
        self._level = 1
        self._mole_appeared = 0

    def update(
        self,
        lives: int,
        score: int,
        checkpoint_score: int,
        checkpoint_total: int,
        level: int = 1,
    ) -> None:
        self._lives = lives
        self._score = score
        self._checkpoint_score = checkpoint_score
        self._checkpoint_total = checkpoint_total
        self._level = level

    def set_click(self, x: int, y: int) -> None:
        """Record a click position to display in UI."""
        self._click_pos = (x, y)
        self._click_frames = 8  # Show click for 8 frames

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape

        # Show click cursor (bright circle that fades)
        if self._click_pos and self._click_frames > 0:
            cx, cy = self._click_pos
            # Scale to 64x64 display
            cx = cx * 2 + 1
            cy = cy * 2 + 1
            if 0 <= cx < w and 0 <= cy < h:
                # Draw bright cyan circle
                for r in range(2, 6):
                    for ox, oy in [
                        (0, -r),
                        (0, r),
                        (-r, 0),
                        (r, 0),
                        (-r, -r),
                        (-r, r),
                        (r, -r),
                        (r, r),
                    ]:
                        px, py = cx + ox, cy + oy
                        if 0 <= px < w and 0 <= py < h:
                            frame[py, px] = 6  # Cyan
                # Center dot
                frame[cy, cx] = 6
                if cy + 1 < h:
                    frame[cy + 1, cx] = 6
            self._click_frames -= 1
        else:
            self._click_pos = None

        # Level indicator - show current level (1-5)
        frame[2, 2] = 9  # Blue = level marker
        # Use 3 cells to show level number
        level_colors = [9, 6, 3, 4, 7]  # Blue, Cyan, Green, Yellow, Navy
        frame[2, 3] = level_colors[(self._level - 1) % 5]

        # Score - yellow dot, size indicates score
        if self._score > 0:
            frame[2, w - 3] = 4  # Yellow = score
            if self._score > 3:
                frame[2, w - 4] = 4
            if self._score > 6:
                frame[2, w - 5] = 4

        # Lives - red dots on right side (5 = full)
        for i in range(5):
            if i < self._lives:
                frame[h - 3, w - 4 - i] = 2  # Red = alive
            else:
                frame[h - 3, w - 4 - i] = 5  # Gray = lost

        # Checkpoint progress - show as dots that change color:
        # Each checkpoint needs 3 mole appearances
        # Green = whacked, Red = missed/escaped
        if self._checkpoint_total > 0:
            for i in range(3):  # 3 appearances per checkpoint
                if i < self._checkpoint_score:
                    frame[h - 3, 2 + i] = 3  # Green = whacked
                elif i < self._mole_appeared % 3 or self._checkpoint_score == 0:
                    frame[h - 3, 2 + i] = 2  # Red = waiting/missed
                else:
                    frame[h - 3, 2 + i] = 5  # Gray = not yet

        return frame
        h, w = frame.shape

        # Show click cursor briefly (just a flash)
        if self._click_pos and self._click_frames > 0:
            cx, cy = self._click_pos
            if 0 <= cx < w and 0 <= cy < h:
                # Draw a bright cyan circle
                for r in range(4):
                    for angle in range(0, 360, 45):
                        rad = angle * 3.14159 / 180
                        px = int(cx + r * 1.3 * (rad - 3.14159 / 2) / 3)
                        py = int(cy + r)
                        if 0 <= px < w and 0 <= py < h:
                            frame[py, px] = 6  # Cyan
            self._click_frames -= 1
        else:
            self._click_pos = None

        # Show level in top-left with letter L
        frame[2, 2] = 9  # Blue L marker

        # Show score in top-right with S
        score_display = min(self._score, 9)  # Max 9 for single digit
        frame[2, w - 3] = 4 if score_display > 0 else 5  # Yellow if score, gray if 0

        # Show lives as red hearts/markers on right side (5 = full)
        for i in range(5):
            if i < self._lives:
                frame[h - 3, w - 4 - i] = 2  # Red = alive
            else:
                frame[h - 3, w - 4 - i] = 5  # Gray = lost

        # Show checkpoint progress as bar on left side
        # Yellow = needed per checkpoint, Green = achieved
        if self._checkpoint_total > 0:
            for i in range(self._checkpoint_total):
                frame[h - 3, 2 + i] = 4  # Yellow background
            for i in range(min(self._checkpoint_score, self._checkpoint_total)):
                frame[h - 3, 2 + i] = 3  # Green = achieved

        return frame


sprites = {
    "hole": Sprite(
        pixels=[
            [5, 5, 5],
            [5, 0, 5],
            [5, 5, 5],
        ],
        name="hole",
        visible=True,
        collidable=False,
        tags=["hole"],
    ),
    "mole": Sprite(
        pixels=[
            [0, 6, 6, 6, 0],
            [6, 6, 6, 6, 6],
            [6, 6, 8, 6, 6],
            [6, 6, 6, 6, 6],
            [0, 6, 6, 6, 0],
        ],
        name="mole",
        visible=True,
        collidable=False,
        tags=["mole"],
    ),
    "whacked": Sprite(
        pixels=[
            [3, 3, 3],
            [3, 2, 3],
            [3, 3, 3],
        ],
        name="whacked",
        visible=True,
        collidable=False,
        tags=["whacked"],
    ),
}


def create_level(difficulty: int):
    # Spread holes across full 32x32 grid with good spacing
    # Using 3x3 holes, spaced 8 cells apart for visibility
    hole_positions = []
    for row in range(4, 28, 8):  # Rows at y=4, 12, 20
        for col in range(4, 28, 8):  # Cols at x=4, 12, 20
            hole_positions.append((col, row))

    # Add more holes as difficulty increases (3x3 = 9 holes base, +4 per level)
    num_holes = min(9 + difficulty * 4, len(hole_positions))
    level_holes = hole_positions[:num_holes]

    level_sprites = []
    for x, y in level_holes:
        level_sprites.append(sprites["hole"].clone().set_position(x, y))

    return Level(
        sprites=level_sprites,
        grid_size=(32, 32),
        data={
            "difficulty": difficulty,
            "mole_display_time": max(3, 8 - difficulty * 1),
            "mole_interval": max(2, 6 - difficulty),
            "moles_per_checkpoint": 3,
            "required_score": 2,
        },
    )


levels = [create_level(i) for i in range(1, 6)]

BACKGROUND_COLOR = 0
PADDING_COLOR = 4


class Wm01(ARCBaseGame):
    """Whack-a-Mole game - click moles before they disappear!"""

    def __init__(self) -> None:
        self._ui = Wm01UI(5, 0, 0, 3)
        self._ui._level = 1  # Initialize level
        super().__init__(
            "wm01",
            levels,
            Camera(0, 0, 64, 64, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [6],
        )

    def on_set_level(self, level: Level) -> None:
        self._holes = self.current_level.get_sprites_by_tag("hole")
        self._moles = []
        self._lives = 5
        self._score = 0
        self._checkpoint_count = 0
        self._checkpoint_score = 0
        self._mole_appeared = 0
        self._current_mole = None
        self._mole_timer = 0
        self._action_count = 0
        self._difficulty = self.current_level.get_data("difficulty")
        self._mole_display_time = self.current_level.get_data("mole_display_time")
        self._mole_interval = self.current_level.get_data("mole_interval")
        self._moles_per_checkpoint = self.current_level.get_data("moles_per_checkpoint")
        self._required_score = self.current_level.get_data("required_score")
        self._update_ui()

    def _spawn_mole(self):
        if self._current_mole is None and self._holes:
            available_holes = [h for h in self._holes if h not in self._moles]
            if available_holes:
                hole = random.choice(available_holes)
                mole = sprites["mole"].clone().set_position(hole.x, hole.y)
                self.current_level.add_sprite(mole)
                self._moles.append(mole)
                self._current_mole = mole
                self._mole_appeared += 1
                self._mole_timer = 0

    def _hide_mole(self):
        if self._current_mole:
            self.current_level.remove_sprite(self._current_mole)
            if self._current_mole in self._moles:
                self._moles.remove(self._current_mole)
            # Mole escaped - if no whack this appearance, lose a life
            self._moles.append(self._current_mole)  # Mark as escaped
            self._current_mole = None

    def _check_checkpoint(self):
        if (
            self._mole_appeared > 0
            and self._mole_appeared % self._moles_per_checkpoint == 0
        ):
            if self._checkpoint_score < self._required_score:
                self.lose()
                return True
            # Passed checkpoint - advance to next level
            self._checkpoint_count += 1
            self._checkpoint_score = 0
            # Check if we've completed all checkpoints for this level
            total_checkpoints = 3  # 3 checkpoints per level
            if self._checkpoint_count >= total_checkpoints:
                self.next_level()
                # Reset for next level
                self._checkpoint_count = 0
                self._lives = 5  # Reset lives
        return False

    def _update_ui(self):
        level_num = self._checkpoint_count + 1
        self._ui.update(
            self._lives,
            self._score,
            self._checkpoint_score,
            self._moles_per_checkpoint,
            level_num,
        )
        # Also update mole_appeared for checkpoint display
        self._ui._mole_appeared = self._mole_appeared

    def step(self) -> None:
        self._action_count += 1

        # Spawn mole periodically
        if self._current_mole is None:
            if self._action_count % self._mole_interval == 0:
                self._spawn_mole()
        else:
            self._mole_timer += 1
            if self._mole_timer >= self._mole_display_time:
                # Mole disappeared without being whacked - no penalty, just missed opportunity
                self._hide_mole()
                self._check_checkpoint()
                self._update_ui()

        # Handle ACTION6 - click to whack
        if self.action.id.value == 6:
            x = self.action.data.get("x", 0)
            y = self.action.data.get("y", 0)

            # Show click cursor in UI
            self._ui.set_click(x, y)

            # Convert display coords to grid coords
            grid_x = x // 2
            grid_y = y // 2

            clicked_sprite = self.current_level.get_sprite_at(
                grid_x, grid_y, ignore_collidable=True
            )

            if clicked_sprite and "mole" in clicked_sprite.tags:
                # Whacked the mole!
                self.current_level.remove_sprite(clicked_sprite)
                if clicked_sprite in self._moles:
                    self._moles.remove(clicked_sprite)

                whacked = (
                    sprites["whacked"]
                    .clone()
                    .set_position(clicked_sprite.x, clicked_sprite.y)
                )
                self.current_level.add_sprite(whacked)

                self._score += 1
                self._checkpoint_score += 1

                # Remove whacked marker after short delay
                self._current_mole = None

                self._check_checkpoint()
            # Clicked on empty hole - no penalty

            self._update_ui()

        self.complete_action()
