import logging
import typing

from pyglet_tetris.board.block import BoardBlock
from pyglet_tetris.board.board_printer import BoardPrinter
from pyglet_tetris.board.piece import BoardPiece
from pyglet_tetris.shape import Shape

_logger = logging.getLogger(__name__)


class Board:
    EMPTY_SPACE = ' '

    _active_piece: typing.Union[None, BoardPiece]

    def __init__(self, width, height, print_board=True):
        self._board = [[self.EMPTY_SPACE for _ in range(height)] for _ in range(width)]
        self.height = height
        self.width = width
        self._active_piece = None
        self._game_over = False
        self._spawn_position = BoardBlock(self.width // 2 - 2, 0)
        self._print_board = print_board
        self._board_printer = BoardPrinter(self._board, width, height)

    def move_right(self):
        self._move_active_piece(1)

    def move_left(self):
        self._move_active_piece(-1)

    def _move_active_piece(self, direction_offset):
        if not self._active_piece:
            raise RuntimeError("No active piece")

        _logger.debug(f"Moving piece by x={direction_offset}")
        new_piece = self._active_piece.copy()
        new_piece.move(x=direction_offset)
        if self._is_legal_position(new_piece, self._active_piece):
            self._move_piece(self._active_piece, new_piece)
            _logger.debug(f"Piece moved to: {self._active_piece}")
            self._active_piece = new_piece

        if self._print_board:
            self._board_printer.print_to_console()

    def drop(self):
        if self._active_piece:
            _logger.debug(f"Dropping piece")
            moved_piece = self._active_piece.copy()
            moved_piece.move(y=1)
            if self._is_legal_position(moved_piece, self._active_piece):
                _logger.debug(f"Piece dropped to: {self._active_piece}")
                self._move_piece(self._active_piece, moved_piece)
                self._active_piece = moved_piece
            else:
                self._active_piece = None

        if self._print_board:
            self._board_printer.print_to_console()

    def full_drop(self):
        cells_dropped = 0
        while self._active_piece:
            self.drop()
            cells_dropped += 1
        return cells_dropped

    def is_game_over(self):
        return self._game_over

    def is_piece_active(self):
        return self._active_piece is not None

    def any_rows_completed(self) -> bool:
        return len(self._calc_completed_rows()) > 0

    def clear_completed_rows(self) -> int:
        completed_rows = self._calc_completed_rows()
        _logger.info(f"Clearing {len(completed_rows)} lines")
        _logger.debug(f"Clearing rows: {completed_rows}")
        for row_number in completed_rows[::-1]:
            _logger.debug(f"Clearing row {row_number}")
            for col in range(self.width):
                self._board[col][row_number] = self.EMPTY_SPACE
        self._skip_empty_rows()
        return len(completed_rows)

    def _calc_completed_rows(self) -> typing.List[int]:
        completed_rows = [self._is_row_full(row) for row in self._transposed_board()]
        return [i for i, row_completed, in enumerate(completed_rows) if row_completed]

    def _calc_empty_rows(self):
        completed_rows = [self._is_row_empty(row) for row in self._transposed_board()]
        return [i for i, row_completed, in enumerate(completed_rows) if row_completed]

    def _transposed_board(self):
        return [*zip(*self._board)][::]

    def _skip_empty_rows(self):
        # from bottom to top
        swapped = True
        transposed_board = self._transposed_board()
        while swapped:
            swapped = False
            row_number = self.height - 1
            while row_number > 1:
                if self._is_row_empty(transposed_board[row_number]) and \
                        not self._is_row_empty(transposed_board[row_number - 1]):
                    _logger.debug(f"Swapping rows {row_number}, {row_number - 1}")
                    self._swap_rows(row_number, row_number - 1)
                    transposed_board = self._transposed_board()
                    swapped = True
                row_number -= 1

    def _swap_rows(self, row_num_a, row_num_b):
        for col in range(self.width):
            self._board[col][row_num_a], self._board[col][row_num_b] = \
                self._board[col][row_num_b], self._board[col][row_num_a]

    def _is_row_empty(self, row):
        return all([self.EMPTY_SPACE == b for b in row])

    def _is_row_full(self, row):
        return self.EMPTY_SPACE not in row

    def spawn_piece(self, piece: Shape):
        new_piece = [BoardBlock(x, y) + self.spawn_position for (x, y) in piece.cords]
        center = BoardBlock(piece.center[0], piece.center[1]) + self.spawn_position
        new_piece = BoardPiece(piece, new_piece, center)
        _logger.info(f"Spawning new piece: {new_piece.shape.__name__}")
        _logger.debug(f"Spawning new piece: {new_piece}")

        if not self._is_legal_position(new_piece):
            _logger.info("Illegal start position, ending game")
            self._game_over = True

        self._active_piece = new_piece
        self._move_piece(None, self._active_piece)

    def get_blocks(self) -> typing.Dict[typing.Tuple[int, int], str]:
        blocks = {}
        for i, column in enumerate(self._board):
            for j, cell in enumerate(column):
                if cell != self.EMPTY_SPACE:
                    blocks[(i, j)] = cell
        return blocks

    def rotate(self):
        if self._active_piece:
            new_piece = self._active_piece.copy()
            new_piece.rotate()
            if self._is_legal_position(new_piece, self._active_piece):
                self._move_piece(self._active_piece, new_piece)
                self._active_piece = new_piece

    @property
    def spawn_position(self) -> BoardBlock:
        return self._spawn_position

    @spawn_position.setter
    def spawn_position(self, value: BoardBlock):
        self._spawn_position = value

    def _move_piece(self, old_piece, new_piece):
        if old_piece:
            for block in old_piece:
                self._board[block.x][block.y] = self.EMPTY_SPACE
        for block in new_piece:
            self._board[block.x][block.y] = new_piece.id

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
