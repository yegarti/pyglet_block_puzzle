import logging
import time

import pyglet

from pyglet_tetris.block import Block
from pyglet_tetris.board import Board
from pyglet_tetris.shape import ShapeHelper


_logger = logging.getLogger(__name__)


class Game:

    MOVE_SPEED_IN_SECONDS = 1 / 200.0
    CONTINUES_MOVE_DELAY_IN_SECONDS = 1 / 20.0
    DROP_SPEED_IN_SECONDS = 7 / 10.0

    def __init__(self, width, height, block_size, batch):
        self.block_size = block_size
        self.width = width
        self.height = height
        self.piece_maker = ShapeHelper()
        self.batch = batch
        self.key_handler = pyglet.window.key.KeyStateHandler()
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
            self._score_and_clear_completed_lines()
            self._spawn_new_piece()

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
        pyglet.clock.schedule_interval(self.fall, self.DROP_SPEED_IN_SECONDS)
        pyglet.clock.schedule_interval(self.move, self.MOVE_SPEED_IN_SECONDS)

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
        if symbol == pyglet.window.key.UP:
            self.board.rotate()
        if symbol == pyglet.window.key.SPACE:
            self.board.full_drop()

    def move(self, dt):
        if self._paused or self._is_move_continuous():
            return
        moved = False
        if self.board.is_piece_active():
            if self.key_handler[pyglet.window.key.RIGHT]:
                self.board.move_right()
                moved = True
            if self.key_handler[pyglet.window.key.LEFT]:
                self.board.move_left()
                moved = True
            if self.key_handler[pyglet.window.key.DOWN]:
                self._reset_clocks()
                self.board.drop()
                moved = True
        if moved:
            self._latest_move = time.time()

    def _is_move_continuous(self):
        return time.time() - self._latest_move < Game.CONTINUES_MOVE_DELAY_IN_SECONDS

    def fall(self, dt):
        self.board.drop()

    def _reset_clocks(self):
        self._unschedule_clocks()
        self._schedule_clocks()

    def _score_and_clear_completed_lines(self):
        if self.board.any_rows_completed():
            _logger.debug("Scoring lines")
            self.board.clear_completed_rows()
