import logging
import time

import pyglet

from pyglet.window import key
from pyglet_tetris.block import Block
from pyglet_tetris.board import Board
from pyglet_tetris.shape import ShapeHelper


_logger = logging.getLogger(__name__)


class Game:

    MOVE_SPEED_IN_SECONDS = 1 / 200.0
    CONTINUES_MOVE_DELAY_IN_SECONDS = 1 / 20.0
    DROP_SPEED_IN_SECONDS = 7 / 10.0
    SCORE_LINES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
    SCORE_SOFT_DROP = 1
    SCORE_HARD_DROP = 2

    def __init__(self, width, height, block_size, batch):
        self.block_size = block_size
        self.width = width
        self.height = height
        self.piece_maker = ShapeHelper()
        self.batch = batch
        self.key_handler = key.KeyStateHandler()
        self.blocks = []
        self._latest_move = time.time()
        self._paused = False
        self._score = 0
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
        self.piece_maker.reset()
        self._paused = False
        self._score = 0
        self._level = 1
        self.game_over = False
        self._spawn_new_piece()
        self._unschedule_clocks()
        self._schedule_clocks()

    @property
    def level(self):
        return self._level

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score
        _logger.debug(f"New score: {self._score}")

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
        if symbol == key.UP or symbol == key.W:
            self.board.rotate()
        if symbol == key.SPACE:
            self.score += self.board.full_drop() * self.SCORE_HARD_DROP

    def move(self, dt):
        if self._paused or self._is_move_continuous():
            return
        moved = False
        if self.board.is_piece_active():
            if self.key_handler[key.RIGHT] or self.key_handler[key.D]:
                self.board.move_right()
                moved = True
            if self.key_handler[key.LEFT] or self.key_handler[key.A]:
                self.board.move_left()
                moved = True
            if self.key_handler[key.DOWN] or self.key_handler[key.S]:
                self.soft_drop()
                moved = True
        if moved:
            self._latest_move = time.time()

    def _is_move_continuous(self):
        return time.time() - self._latest_move < Game.CONTINUES_MOVE_DELAY_IN_SECONDS

    def soft_drop(self):
        self._reset_clocks()
        self.board.drop()
        self.score += self.SCORE_SOFT_DROP

    def fall(self, dt):
        self.board.drop()

    def _reset_clocks(self):
        self._unschedule_clocks()
        self._schedule_clocks()

    def _score_and_clear_completed_lines(self):
        if self.board.any_rows_completed():
            full_rows = self.board.clear_completed_rows()
            _logger.debug(f"Scoring for {full_rows} rows")
            self.score += self._level * self.SCORE_LINES[full_rows]
