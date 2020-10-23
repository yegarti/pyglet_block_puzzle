import random
from abc import abstractmethod

from pyglet_tetris.color import Color


class Shape:
    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def cords(self):
        pass

    @property
    @abstractmethod
    def center(self):
        pass

    @property
    @abstractmethod
    def color(self):
        pass


class Square(Shape):
    id = 'O'
    cords = ((0, 0),
             (1, 0),
             (0, 1),
             (1, 1))
    center = (0.5, 0.5)
    color = Color.YELLOW


class Straight(Shape):
    id = 'I'
    cords = ((0, 0),
             (1, 0),
             (2, 0),
             (3, 0))
    center = (2, 0)
    color = Color.TURQUOISE


class Ra(Shape):
    id = 'L'
    cords = ((0, 0),
             (1, 0),
             (1, 1),
             (1, 2))
    center = (1, 1)
    color = Color.BLUE


class Ri(Shape):
    id = 'R'
    cords = ((0, 0),
             (0, 1),
             (0, 2),
             (1, 0))
    center = (0, 1)
    color = Color.ORANGE


class Ss(Shape):
    id = 'S'
    cords = ((0, 0),
             (1, 0),
             (1, 1),
             (2, 1))
    center = (1, 0.5)
    color = Color.GREEN


class Zed(Shape):
    id = 'Z'
    cords = ((0, 1),
             (1, 1),
             (1, 0),
             (2, 0))
    center = (1, 0.5)
    color = Color.RED


class Ti(Shape):
    id = 'T'
    cords = ((0, 0),
             (1, 0),
             (1, 1),
             (2, 0))
    center = (1, 0.5)
    color = Color.PURPLE


class ShapeHelper:
    def __init__(self):
        self._shapes = [
            Square,
            Ra,
            Straight,
            Ri,
            Zed,
            Ti,
            Ss,
        ]
        self._ids_shapes = {shape.id: shape for shape in self._shapes}

    def get_shape_from_id(self, shape_id) -> Shape:
        return self._ids_shapes[shape_id]

    def get_random_shape(self):
        return random.choice(self._shapes)
