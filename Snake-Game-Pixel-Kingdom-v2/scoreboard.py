"""Score, overlays, board art, and high-score persistence."""

from __future__ import annotations

from pathlib import Path
from turtle import Turtle

# Retro platformer-inspired palette.
BACKGROUND = "#5C94FC"
BOARD_FILL = "#FCE8A6"
BORDER = "#7A3E13"
INNER_BORDER = "#FBD000"
GRID = "#E5B65D"
TEXT = "#FFFFFF"
MUTED = "#FFF2C5"
RED = "#E52521"
BLUE = "#049CD8"
YELLOW = "#FBD000"
GREEN = "#43B047"
BROWN = "#7A3E13"
SHADOW = "#3A5FA0"
ACCENT = RED
CYAN = BLUE
PINK = RED


class HighScoreStore:
    """Load and save a local high score without failing if storage is unavailable."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> int:
        try:
            return max(0, int(self.path.read_text(encoding="utf-8").strip()))
        except (FileNotFoundError, ValueError, OSError):
            return 0

    def save(self, score: int) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(str(max(0, score)), encoding="utf-8")
        except OSError:
            # The game remains fully playable even in a read-only folder.
            pass


class GameUI:
    """Draw the static board and manage all on-screen text."""

    def __init__(
        self,
        screen_width: int,
        play_left: int,
        play_right: int,
        play_bottom: int,
        play_top: int,
    ) -> None:
        self.screen_width = screen_width
        self.play_left = play_left
        self.play_right = play_right
        self.play_bottom = play_bottom
        self.play_top = play_top

        self.board_pen = self._new_pen()
        self.title_pen = self._new_pen()
        self.score_pen = self._new_pen()
        self.status_pen = self._new_pen()
        self.overlay_pen = self._new_pen()
        self.hint_pen = self._new_pen()

        self._draw_board()
        self._draw_header()

    @staticmethod
    def _new_pen() -> Turtle:
        pen = Turtle(visible=False)
        pen.penup()
        pen.speed("fastest")
        return pen

    @staticmethod
    def _draw_filled_rectangle(
        pen: Turtle,
        left: float,
        bottom: float,
        right: float,
        top: float,
        fill: str,
        outline: str,
        width: int,
    ) -> None:
        pen.goto(left, bottom)
        pen.setheading(0)
        pen.pencolor(outline)
        pen.fillcolor(fill)
        pen.pensize(width)
        pen.pendown()
        pen.begin_fill()

        for point in (
            (right, bottom),
            (right, top),
            (left, top),
            (left, bottom),
        ):
            pen.goto(point)

        pen.end_fill()
        pen.penup()

    def _draw_board(self) -> None:
        pen = self.board_pen

        # Warm play area against the blue sky background.
        self._draw_filled_rectangle(
            pen,
            self.play_left,
            self.play_bottom,
            self.play_right,
            self.play_top,
            BOARD_FILL,
            BORDER,
            5,
        )

        # Soft square grid keeps the original gameplay easy to read.
        pen.pencolor(GRID)
        pen.pensize(1)

        for x in range(self.play_left, self.play_right + 1, 40):
            pen.goto(x, self.play_bottom)
            pen.pendown()
            pen.goto(x, self.play_top)
            pen.penup()

        for y in range(self.play_bottom, self.play_top + 1, 40):
            pen.goto(self.play_left, y)
            pen.pendown()
            pen.goto(self.play_right, y)
            pen.penup()

        # Bright inner line creates a cheerful arcade-frame effect.
        inset = 7
        pen.pencolor(INNER_BORDER)
        pen.pensize(2)
        pen.goto(self.play_left + inset, self.play_bottom + inset)
        pen.pendown()

        for point in (
            (self.play_right - inset, self.play_bottom + inset),
            (self.play_right - inset, self.play_top - inset),
            (self.play_left + inset, self.play_top - inset),
            (self.play_left + inset, self.play_bottom + inset),
        ):
            pen.goto(point)

        pen.penup()

        # Small brick-like blocks below the board add a retro platformer feel.
        brick_y = self.play_bottom - 30
        brick_width = 56
        start_x = self.play_left

        for index in range(11):
            left = start_x + index * brick_width
            right = min(left + brick_width - 3, self.play_right)
            if left >= self.play_right:
                break

            fill = "#C96B2C" if index % 2 == 0 else "#E58A3A"
            self._draw_filled_rectangle(
                pen,
                left,
                brick_y,
                right,
                brick_y + 18,
                fill,
                BORDER,
                2,
            )

    def _draw_header(self) -> None:
        title_x = -self.screen_width // 2 + 40

        # Simple offset shadow gives the title a arcade look.
        self.title_pen.goto(title_x + 3, 355)
        self.title_pen.color(SHADOW)
        self.title_pen.write(
            "PIXEL KINGDOM SNAKE",
            align="left",
            font=("Courier", 21, "bold"),
        )

        self.title_pen.goto(title_x, 359)
        self.title_pen.color(RED)
        self.title_pen.write(
            "PIXEL KINGDOM SNAKE",
            align="left",
            font=("Courier", 21, "bold"),
        )

        self.hint_pen.goto(0, -390)
        self.hint_pen.color(TEXT)
        self.hint_pen.write(
            "ARROWS / WASD  Move     SPACE  Start     P  Pause     R  Restart     ESC  Exit",
            align="center",
            font=("Courier", 9, "bold"),
        )

    def update_score(self, score: int, high_score: int, speed_level: int) -> None:
        self.score_pen.clear()
        self.score_pen.goto(self.screen_width // 2 - 40, 360)
        self.score_pen.color(YELLOW)
        self.score_pen.write(
            f"SCORE  {score:02d}   BEST  {high_score:02d}   SPEED  {speed_level}",
            align="right",
            font=("Courier", 12, "bold"),
        )

    def set_status(self, text: str, colour: str = ACCENT) -> None:
        self.status_pen.clear()
        self.status_pen.goto(0, 327)
        self.status_pen.color(colour)
        self.status_pen.write(
            text,
            align="center",
            font=("Courier", 10, "bold"),
        )

    def show_ready(self) -> None:
        self.show_overlay(
            "READY?",
            "Press SPACE to begin\nCollect the golden coins and avoid the walls and your tail.",
            RED,
        )
        self.set_status("WAITING TO START", YELLOW)

    def show_paused(self) -> None:
        self.show_overlay("PAUSED", "Press P to continue", BLUE)
        self.set_status("GAME PAUSED", YELLOW)

    def show_game_over(self, score: int, new_best: bool) -> None:
        subtitle = f"Final score: {score}\nPress SPACE or R to play again"

        if new_best:
            subtitle = f"NEW HIGH SCORE: {score}\nPress SPACE or R to play again"

        self.show_overlay("GAME OVER", subtitle, RED)
        self.set_status("RUN ENDED", YELLOW)

    def show_overlay(self, title: str, subtitle: str, colour: str) -> None:
        self.overlay_pen.clear()

        # Offset shadow keeps text readable on the warm board.
        self.overlay_pen.goto(3, 39)
        self.overlay_pen.color(BROWN)
        self.overlay_pen.write(
            title,
            align="center",
            font=("Courier", 28, "bold"),
        )

        self.overlay_pen.goto(0, 43)
        self.overlay_pen.color(colour)
        self.overlay_pen.write(
            title,
            align="center",
            font=("Courier", 28, "bold"),
        )

        self.overlay_pen.goto(0, -22)
        self.overlay_pen.color(BROWN)
        self.overlay_pen.write(
            subtitle,
            align="center",
            font=("Courier", 11, "bold"),
        )

    def clear_overlay(self) -> None:
        self.overlay_pen.clear()
