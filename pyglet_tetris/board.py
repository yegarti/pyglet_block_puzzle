import logging
import typing
from copy import copy
from dataclasses import dataclass

from pyglet_tetris.shape import Shape

_logger = logging.getLogger(__name__)


@dataclass
class BoardBlock:
    x: int
    y: int

    def __add__(self, other):
        return BoardBlock(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self


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
            block.x, block.y = int(block.x), int(block.y)

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


class Board:
    EMPTY_SPACE = ' '

    _active_piece: typing.Union[None, BoardPiece]

    def __init__(self, width, height):
        self._board = [[self.EMPTY_SPACE for _ in range(height)] for _ in range(width)]
        self.height = height
        self.width = width
        self._active_piece = None
        self._game_over = False

    def move_right(self):
        self._move_active_piece(1)

    def move_left(self):
        self._move_active_piece(-1)

    def _move_active_piece(self, direction_offset):
        if not self._active_piece:
            raise RuntimeError("No active piece")

        _logger.info(f"Moving piece by x={direction_offset}")
        new_piece = self._active_piece.copy()
        new_piece.move(x=direction_offset)
        if self._is_legal_position(new_piece, self._active_piece):
            self._move_piece(self._active_piece, new_piece)
            _logger.debug(f"Piece moved to: {self._active_piece}")
            self._active_piece = new_piece

        self._print_board()

    def drop(self):
        if self._active_piece:
            _logger.info(f"Dropping piece")
            moved_piece = self._active_piece.copy()
            moved_piece.move(y=1)
            if self._is_legal_position(moved_piece, self._active_piece):
                _logger.debug(f"Piece dropped to: {self._active_piece}")
                self._move_piece(self._active_piece, moved_piece)
                self._active_piece = moved_piece
            else:
                self._active_piece = None
        self._print_board()

    def full_drop(self):
        while self._active_piece:
            self.drop()

    def is_game_over(self):
        return self._game_over

    def is_piece_active(self):
        return self._active_piece is not None

    def spawn_piece(self, piece: Shape):
        spawn_position = BoardBlock(self.width // 2 - 2, 0)
        new_piece = [BoardBlock(x, y) + spawn_position for (x, y) in piece.cords]
        center = BoardBlock(piece.center[0], piece.center[1]) + spawn_position
        new_piece = BoardPiece(piece, new_piece, center)
        _logger.info(f"Spawning new piece: {new_piece}")

        if not self._is_legal_position(new_piece):
            _logger.info("Illegal start position, ending game")
            self._game_over = True

        self._active_piece = new_piece
        self._move_piece(None, self._active_piece)

    def get_blocks(self):
        blocks = {}
        for i, column in enumerate(self._board):
            for j, cell in enumerate(column):
                if cell != self.EMPTY_SPACE:
                    blocks[(i, j)] = cell
        return blocks

    def rotate(self):
        new_piece = self._active_piece.copy()
        new_piece.rotate()
        if self._is_legal_position(new_piece, self._active_piece):
            self._move_piece(self._active_piece, new_piece)
            self._active_piece = new_piece

    def _move_piece(self, old_piece, new_piece):
        if old_piece:
            for block in old_piece:
                self._board[block.x][block.y] = self.EMPTY_SPACE
        for block in new_piece:
            self._board[block.x][block.y] = new_piece.id

    def _print_board(self):
        for j in range(self.height):
            for i in range(self.width):
                if j == 0 and i == 0:
                    self._print_board_top_header()
                if i == 0:
                    self._print_board_wall()

                cell = self._board[i][j]
                print(f"{cell}", end='')

                if i == self.width - 1:
                    self._print_board_wall()

            print()
        self._print_board_horizontal_header()
        print()

    def _print_board_horizontal_header(self):
        for _ in range(self.width):
            print("-", end='')

    def _print_board_wall(self):
        print('|', end='')

    def _print_board_top_header(self):
        print()
        print("Board")
        self._print_board_horizontal_header()
        print()

    def _is_legal_position(self, target, source=None):
        return self._is_in_boundaries(target) and \
               not self._is_collide(target, ignore=source)

    def _is_in_boundaries(self, piece):
        return all(
            map(lambda block: 0 <= block.x < self.width and 0 <= block.y < self.height,
                piece))

    def _is_collide(self, piece, ignore=None):
        if not ignore:
            ignore = []
        for block in piece:
            cell = self._board[block.x][block.y]
            if cell != self.EMPTY_SPACE and block not in ignore:
                return True
        return False
