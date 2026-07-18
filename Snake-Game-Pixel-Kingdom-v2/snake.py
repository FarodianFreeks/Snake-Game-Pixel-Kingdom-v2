"""Snake body and movement logic for Pixel Kingdom Snake."""

from __future__ import annotations

from turtle import Turtle
from typing import Iterable

GRID_SIZE = 20
STARTING_POSITIONS = [(0, 0), (-GRID_SIZE, 0), (-GRID_SIZE * 2, 0)]

UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

BODY_COLOURS = (
    "#43B047",
    "#63C74D",
    "#2F9E44",
    "#76C442",
    "#3DA35D",
    "#8BC34A",
)


class Snake:
    """A grid-based snake with safe, responsive direction handling."""

    def __init__(self) -> None:
        self.segments: list[Turtle] = []
        self.next_heading = RIGHT
        self.turn_locked = False
        self._create_snake()

    @property
    def head(self) -> Turtle:
        return self.segments[0]

    @property
    def occupied_positions(self) -> list[tuple[int, int]]:
        """Return rounded grid positions currently occupied by the snake."""
        return [
            (round(segment.xcor()), round(segment.ycor()))
            for segment in self.segments
        ]

    def _create_snake(self) -> None:
        for position in STARTING_POSITIONS:
            self._add_segment(position)
        self._refresh_colours()

    def _add_segment(self, position: tuple[float, float]) -> None:
        segment = Turtle("square")
        segment.penup()
        segment.speed("fastest")
        segment.shapesize(stretch_wid=0.86, stretch_len=0.86)
        segment.goto(position)
        self.segments.append(segment)

    def _refresh_colours(self) -> None:
        for index, segment in enumerate(self.segments):
            if index == 0:
                segment.color("#8B1E1A", "#E52521")
                segment.shapesize(stretch_wid=0.92, stretch_len=0.92)
            else:
                colour = BODY_COLOURS[(index - 1) % len(BODY_COLOURS)]
                segment.color("#1F6F35", colour)
                segment.shapesize(stretch_wid=0.86, stretch_len=0.86)

    def move(self) -> None:
        """Move the snake one grid step."""
        for index in range(len(self.segments) - 1, 0, -1):
            previous = self.segments[index - 1]
            self.segments[index].goto(previous.xcor(), previous.ycor())

        self.head.setheading(self.next_heading)
        self.head.forward(GRID_SIZE)
        self.turn_locked = False

    def extend(self) -> None:
        """Add one segment at the tail's current position."""
        tail = self.segments[-1]
        self._add_segment((tail.xcor(), tail.ycor()))
        self._refresh_colours()

    def reset(self) -> None:
        """Restore the snake to its starting position and length."""
        for segment in self.segments:
            segment.hideturtle()
        self.segments.clear()
        self.next_heading = RIGHT
        self.turn_locked = False
        self._create_snake()

    def collides_with_self(self) -> bool:
        """Check whether the head overlaps any body segment."""
        return any(self.head.distance(segment) < 10 for segment in self.segments[1:])

    def set_direction(self, heading: int) -> None:
        """Queue one legal direction change per movement tick."""
        if self.turn_locked:
            return

        current_heading = round(self.head.heading())
        if heading == OPPOSITE_DIRECTIONS.get(current_heading):
            return

        self.next_heading = heading
        self.turn_locked = True

    def up(self) -> None:
        self.set_direction(UP)

    def down(self) -> None:
        self.set_direction(DOWN)

    def left(self) -> None:
        self.set_direction(LEFT)

    def right(self) -> None:
        self.set_direction(RIGHT)
