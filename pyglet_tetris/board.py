import typing

from pyglet_tetris.shape import Shape


class Board:
    EMPTY_SPACE = ' '

    _active_piece: typing.Union[None, Shape]

    def __init__(self, width, height):
        self._board = [[self.EMPTY_SPACE for _ in range(height)] for _ in range(width)]
        self.height = height
        self.width = width
        self._active_piece = None
        self._active_piece_position = None
        self._game_over = False

    def move_right(self):
        self._move_active_piece('right')

    def move_left(self):
        self._move_active_piece('left')

    def _move_active_piece(self, direction):
        if not self._active_piece:
            raise RuntimeError("No active piece")
        if direction == 'left':
            offset = -1
        elif direction == 'right':
            offset = 1
        else:
            raise KeyError(f"Unknown direction {direction}")

        old_piece = self._active_piece_position
        new_piece = [(x + offset, y) for (x, y) in old_piece]
        if self._is_legal_position(new_piece, old_piece):
            self._move_piece(old_piece, new_piece, self._active_piece.id)
            self._active_piece_position = new_piece

        self._print_board()

    def drop(self):
        if self._active_piece:
            old_piece = self._active_piece_position
            new_piece = [(x, y+1) for (x, y) in old_piece]
            if self._is_legal_position(new_piece, old_piece):
                self._move_piece(old_piece, new_piece, self._active_piece.id)
                self._active_piece_position = new_piece
            else:
                self._active_piece = None
        self._print_board()

    def rotate(self):
        pass

    def is_game_over(self):
        return self._game_over

    def is_piece_active(self):
        return self._active_piece is not None

    def spawn_piece(self, piece: Shape):
        spawn_position = (self.width // 2 - 2, 0)
        new_piece = [(x + spawn_position[0], y + spawn_position[1]) for (x, y) in piece.cords]
        if not self._is_legal_position(new_piece):
            self._game_over = True
        self._move_piece(None, new_piece, piece.id)
        self._active_piece = piece
        self._active_piece_position = new_piece

    def get_blocks(self):
        blocks = {}
        for i, column in enumerate(self._board):
            for j, cell in enumerate(column):
                if cell != self.EMPTY_SPACE:
                    blocks[(i, j)] = cell
        return blocks

    def _move_piece(self, old_piece, new_piece, new_piece_id):
        if old_piece:
            for (x, y) in old_piece:
                self._board[x][y] = self.EMPTY_SPACE
        for (x, y) in new_piece:
            self._board[x][y] = new_piece_id

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
            map(lambda block: 0 <= block[0] < self.width and block[1] < self.height,
                piece))

    def _is_collide(self, piece, ignore=None):
        if not ignore:
            ignore = []
        for block in piece:
            cell = self._board[block[0]][block[1]]
            if cell != self.EMPTY_SPACE and block not in ignore:
                return True
        return False
