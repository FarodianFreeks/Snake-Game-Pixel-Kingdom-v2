"""Entry point for the modernised Pixel Kingdom Snake game."""

from __future__ import annotations

from pathlib import Path
from turtle import Screen, Terminator

from food import Food
from scoreboard import BACKGROUND, GameUI, HighScoreStore
from snake import GRID_SIZE, Snake

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 820

PLAY_LEFT = -320
PLAY_RIGHT = 320
PLAY_BOTTOM = -320
PLAY_TOP = 300

BASE_DELAY_MS = 115
MIN_DELAY_MS = 55
SPEED_STEP_MS = 5
POINTS_PER_SPEED_LEVEL = 3

READY = "ready"
RUNNING = "running"
PAUSED = "paused"
GAME_OVER = "game_over"


class SnakeGame:
    """Coordinate the screen, input, game state, score, and update loop."""

    def __init__(self) -> None:
        self.screen = Screen()
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.bgcolor(BACKGROUND)
        self.screen.title("Pixel Kingdom Snake")
        self.screen.tracer(0)

        self.snake = Snake()
        self.food = Food(
            x_limit=PLAY_RIGHT - GRID_SIZE,
            y_min=PLAY_BOTTOM + GRID_SIZE,
            y_max=PLAY_TOP - GRID_SIZE,
            grid_size=GRID_SIZE,
        )
        self.food.refresh(self.snake.occupied_positions)

        self.ui = GameUI(
            SCREEN_WIDTH,
            PLAY_LEFT,
            PLAY_RIGHT,
            PLAY_BOTTOM,
            PLAY_TOP,
        )

        data_file = Path(__file__).resolve().parent / "data" / "high_score.txt"
        self.high_score_store = HighScoreStore(data_file)
        self.high_score = self.high_score_store.load()
        self.run_started_high_score = self.high_score
        self.score = 0
        self.state = READY
        self.loop_active = True
        self.pulse_counter = 0

        self._bind_keys()
        self._refresh_ui()
        self.ui.show_ready()
        self.screen.update()
        self.screen.ontimer(self._game_tick, BASE_DELAY_MS)

    def _bind_keys(self) -> None:
        self.screen.listen()

        for key in ("Up", "w", "W"):
            self.screen.onkeypress(self.snake.up, key)
        for key in ("Down", "s", "S"):
            self.screen.onkeypress(self.snake.down, key)
        for key in ("Left", "a", "A"):
            self.screen.onkeypress(self.snake.left, key)
        for key in ("Right", "d", "D"):
            self.screen.onkeypress(self.snake.right, key)

        self.screen.onkeypress(self.start_or_restart, "space")
        self.screen.onkeypress(self.toggle_pause, "p")
        self.screen.onkeypress(self.toggle_pause, "P")
        self.screen.onkeypress(self.restart, "r")
        self.screen.onkeypress(self.restart, "R")
        self.screen.onkeypress(self.close, "Escape")

    @property
    def speed_level(self) -> int:
        return 1 + self.score // POINTS_PER_SPEED_LEVEL

    @property
    def current_delay(self) -> int:
        reduction = (self.speed_level - 1) * SPEED_STEP_MS
        return max(MIN_DELAY_MS, BASE_DELAY_MS - reduction)

    def start_or_restart(self) -> None:
        if self.state == READY:
            self.state = RUNNING
            self.ui.clear_overlay()
            self.ui.set_status("RUNNING")
        elif self.state == GAME_OVER:
            self.restart()

    def restart(self) -> None:
        self.run_started_high_score = self.high_score
        self.score = 0
        self.snake.reset()
        self.food.refresh(self.snake.occupied_positions)
        self.state = RUNNING
        self.ui.clear_overlay()
        self.ui.set_status("RUNNING")
        self._refresh_ui()
        self.screen.update()

    def toggle_pause(self) -> None:
        if self.state == RUNNING:
            self.state = PAUSED
            self.ui.show_paused()
        elif self.state == PAUSED:
            self.state = RUNNING
            self.ui.clear_overlay()
            self.ui.set_status("RUNNING")
        self.screen.update()

    def _game_tick(self) -> None:
        if not self.loop_active:
            return

        try:
            if self.state == RUNNING:
                self.snake.move()
                self._handle_food_collision()
                self._handle_terminal_collisions()

            self.pulse_counter += 1
            if self.pulse_counter % 4 == 0:
                self.food.pulse()

            self.screen.update()
            self.screen.ontimer(self._game_tick, self.current_delay)
        except Terminator:
            self.loop_active = False

    def _handle_food_collision(self) -> None:
        if self.snake.head.distance(self.food) >= 16:
            return

        self.snake.extend()
        self.score += 1

        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_store.save(self.high_score)

        self.food.refresh(self.snake.occupied_positions)
        self._refresh_ui()

    def _handle_terminal_collisions(self) -> None:
        x = self.snake.head.xcor()
        y = self.snake.head.ycor()

        hit_wall = (
            x < PLAY_LEFT + GRID_SIZE / 2
            or x > PLAY_RIGHT - GRID_SIZE / 2
            or y < PLAY_BOTTOM + GRID_SIZE / 2
            or y > PLAY_TOP - GRID_SIZE / 2
        )

        if hit_wall or self.snake.collides_with_self():
            self._end_game()

    def _end_game(self) -> None:
        new_best = self.score > self.run_started_high_score

        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_store.save(self.high_score)

        self.state = GAME_OVER
        self._refresh_ui()
        self.ui.show_game_over(self.score, new_best)

    def _refresh_ui(self) -> None:
        self.ui.update_score(self.score, self.high_score, self.speed_level)

    def close(self) -> None:
        self.loop_active = False
        try:
            self.screen.bye()
        except Terminator:
            pass

    def run(self) -> None:
        self.screen.mainloop()


if __name__ == "__main__":
    SnakeGame().run()
