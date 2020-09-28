import typing
from abc import abstractmethod
from enum import Enum

import pyglet

from pyglet_tetris.color import Color


class Tetromino(Enum):
    Square = 'square'
    Straight = 'straight'
    Ra = 'ra'


class Shape:
    def __init__(self, x, y, size, batch=None):
        self.blocks = []
        for cord in self.cords:
            rect = pyglet.shapes.Rectangle(x,
                                           y,
                                           size,
                                           size,
                                           self.color.value,
                                           batch=batch)
            rect.anchor_x = - (cord[0] - self.center[0]) * size
            rect.anchor_y = - (cord[1] - self.center[1]) * size
            self.blocks.append(rect)
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        offset = value - self._x
        for block in self.blocks:
            block.x += offset
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        offset = value - self._y
        for block in self.blocks:
            block.y += offset
        self._y = value

    def rotate(self):
        for block in self.blocks:
            block.rotation += 90

    @property
    @abstractmethod
    def cords(self) -> typing.List[typing.Tuple]:
        pass

    @property
    @abstractmethod
    def center(self) -> typing.List[typing.Tuple]:
        pass

    @property
    @abstractmethod
    def color(self) -> Color:
        pass


class ShapeMaker:
    def __init__(self, size, batch=None):
        self.size = size
        self.batch = batch

    def new(self, x, y, shape) -> Shape:
        if shape == Tetromino.Straight:
            return Straight(x, y, self.size, batch=self.batch)
        if shape == Tetromino.Square:
            return Square(x, y, self.size, batch=self.batch)
        if shape == Tetromino.Ra:
            return Ra(x, y, self.size, batch=self.batch)
        else:
            raise ValueError(f"Unknown shape: {shape}")


class Square(Shape):
    cords = [(0, 0),
             (1, 0),
             (0, 1),
             (1, 1)]
    center = (1, 1)
    color = Color.RED


class Straight(Shape):
    cords = [(0, 0),
             (1, 0),
             (2, 0),
             (3, 0)]
    center = (2, 0)
    color = Color.BLUE


class Ra(Shape):
    cords = [(0, 0),
             (1, 0),
             (1, 1),
             (1, 2)]
    center = (1, 1)
    color = Color.ORANGE
