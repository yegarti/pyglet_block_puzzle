import pyglet
from pyglet_block_puzzle.color import Color


class Block(pyglet.shapes.Rectangle):
    def __init__(self, color: Color, *args, **kwargs):
        super().__init__(color=color.value, *args, **kwargs)
