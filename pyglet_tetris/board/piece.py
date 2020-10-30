import logging
import typing
from copy import copy
from dataclasses import dataclass
from math import floor

from pyglet_tetris.board.block import BoardBlock
from pyglet_tetris.shape import Shape


_logger = logging.getLogger(__name__)


@dataclass
class BoardPiece:
    _shape: Shape
    _blocks: typing.List[BoardBlock]
    _center: BoardBlock

    @property
    def id(self):
        return self._shape.id

    @property
    def blocks(self):
        return [BoardBlock(b.x, b.y) for b in self._blocks]

    @property
    def center(self):
        return BoardBlock(self._center.x, self._center.y)

    @property
    def shape(self):
        return self._shape

    def move(self, x=0, y=0):
        for block in self._blocks:
            block += BoardBlock(x, y)
        self._center += BoardBlock(x, y)

    def rotate(self):
        _logger.debug(f"Rotating piece")
        current_pos = copy(self)
        old_center = current_pos.center
        current_pos.move(-old_center.x, -old_center.y)
        for block in current_pos._blocks:
            block.x, block.y = -block.y, block.x
        current_pos.move(old_center.x, old_center.y)
        for block in current_pos._blocks:
            block.x, block.y = floor(block.x), floor(block.y)

        self._blocks = current_pos._blocks
        self._center = old_center
        _logger.debug(f"Rotated piece position: {self}")

    def __iter__(self):
        def foo():
            for block in self._blocks:
                yield block
        return foo()

    def copy(self):
        return BoardPiece(self._shape,
                          self.blocks,
                          BoardBlock(self._center.x, self._center.y))