import time

import pyglet

from pyglet_tetris.block import Block
from pyglet_tetris.board import Board
from pyglet_tetris.shape import ShapeHelper


class Game:

    MOVE_DELTA = 0.05

    def __init__(self, width, height, block_size, batch):
        self.block_size = block_size
        self.width = width
        self.height = height
        self.piece_maker = ShapeHelper()
        self.batch = batch
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.block_fall_speed_in_seconds = 0.1
        self.blocks = []
        self._latest_move = time.time()
        self._paused = False
        self.game_over = False
        self.reset()

    def update(self, dt):
        self._redraw_pieces()
        if self.board.is_game_over():
            self.game_over = True
        elif not self.board.is_piece_active():
            self._spawn_new_piece()
        self.move(dt)

    def _spawn_new_piece(self):
        tetromino = self.piece_maker.get_random_shape()
        self.board.spawn_piece(tetromino)

    def _redraw_pieces(self):
        self.blocks.clear()
        for (x, y), piece_id in self.board.get_blocks().items():
            x = x * self.block_size
            y = self.height - (y * self.block_size)
            block_color = self.piece_maker.get_shape_from_id(piece_id).color
            self.blocks.append(
                Block(block_color, x=x, y=y, width=self.block_size, height=self.block_size, batch=self.batch))

    def _unschedule_clocks(self):
        pyglet.clock.unschedule(self.fall)

    def _schedule_clocks(self):
        pyglet.clock.schedule_interval(self.fall, self.block_fall_speed_in_seconds)

    # noinspection PyAttributeOutsideInit
    def reset(self):
        self.board = Board(self.width // self.block_size,
                           self.height // self.block_size)
        self.blocks.clear()
        self._paused = False
        self.game_over = False
        self._spawn_new_piece()
        self._unschedule_clocks()
        self._schedule_clocks()

    def pause(self):
        if not self._paused:
            self._paused = True
            self._unschedule_clocks()
        else:
            self._paused = False
            self._schedule_clocks()

    def is_paused(self):
        return self._paused
    def on_key_press(self, symbol, modifiers):
        if self._paused:
            return
        # if symbol == key.RIGHT:
        #     self._active_piece.x += self.block_size
        # if symbol == key.LEFT:
        #     self._active_piece.x -= self.block_size
        # if symbol == key.UP:
        #     self._active_piece.rotate()

    def move(self, dt):
        if self._paused:
            return
        if time.time() - self._latest_move < Game.MOVE_DELTA:
            return
        if self.key_handler[pyglet.window.key.RIGHT]:
            self.board.move_active_piece('right')
        if self.key_handler[pyglet.window.key.LEFT]:
            self.board.move_active_piece('left')
        #     for block in self._active_piece:
        #         old_piece = block
        #         new_piece = tuple(map(operator.add, old_piece, (1, 0)))
        #         self.board[old_piece[1]][old_piece[0]] = 0
        #         self.board[new_piece[1]][new_piece[0]] = 1
        # elif self.key_handler[pyglet.window.key.LEFT]:
        #     self._active_piece[0] -= (1, 0)
        # else:
        #     return
        # self._print_board()
        self._latest_move = time.time()

    def fall(self, dt):
        # self._active_piece.y -= self.block_size
        self.board.fall()
