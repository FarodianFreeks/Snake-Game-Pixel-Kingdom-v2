"""Golden coin placement and animation for Pixel Kingdom Snake."""

from __future__ import annotations

import random
from turtle import Turtle
from typing import Iterable


class Food(Turtle):
    """A golden coin that always spawns on an unoccupied grid cell."""

    def __init__(self, x_limit: int, y_min: int, y_max: int, grid_size: int) -> None:
        super().__init__("circle")
        self.penup()
        self.speed("fastest")
        self.color("#D46A00", "#FBD000")
        self.shapesize(stretch_wid=0.62, stretch_len=0.62)
        self.x_limit = x_limit
        self.y_min = y_min
        self.y_max = y_max
        self.grid_size = grid_size
        self._pulse_large = False

    def refresh(self, occupied_positions: Iterable[tuple[int, int]]) -> None:
        occupied = set(occupied_positions)
        available: list[tuple[int, int]] = []

        for x in range(-self.x_limit, self.x_limit + 1, self.grid_size):
            for y in range(self.y_min, self.y_max + 1, self.grid_size):
                if (x, y) not in occupied:
                    available.append((x, y))

        if available:
            self.goto(random.choice(available))

    def pulse(self) -> None:
        """Apply a small breathing animation without affecting gameplay."""
        self._pulse_large = not self._pulse_large
        size = 0.68 if self._pulse_large else 0.56
        self.shapesize(stretch_wid=size, stretch_len=size)
