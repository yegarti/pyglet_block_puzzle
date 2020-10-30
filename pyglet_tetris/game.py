import logging
import time

import pyglet

from pyglet.window import key
from pyglet_tetris.block import Block
from pyglet_tetris.board.board import Board
from pyglet_tetris.shape import ShapeHelper


_logger = logging.getLogger(__name__)


class Game:

    MOVE_SPEED_IN_SECONDS = 1 / 200.0
    CONTINUES_MOVE_DELAY_IN_SECONDS = 1 / 20.0
    SCORE_LINES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
    SCORE_SOFT_DROP = 1
    SCORE_HARD_DROP = 2
    LINES_PER_LEVEL = 10
    MAX_LEVEL = 20

    def __init__(self, width, height, block_size, batch, text_batch, print_to_console=False):
        self._print_to_console = print_to_console
        self.block_size = block_size
        self.width = width
        self.height = height
        self.piece_maker = ShapeHelper()
        self.batch = batch
        self._text_batch = text_batch
        self.key_handler = key.KeyStateHandler()
        self.blocks = []
        self._latest_move = time.time()
        self._paused = False
        self._game_paused_text = None
        self._cleared_lines = 0
        self._new_level_text = None
        self._score = 0
        self.game_over = False
        self._score_label = pyglet.text.Label(
            f'Score: {self.score}',
            font_name='Times New Roman',
            font_size=18, x=0, y=self.height, batch=self._text_batch, anchor_y='top')
        self.reset()

    def update(self, dt):
        self._redraw_pieces()
        if self.board.is_game_over():
            self.game_over = True
            _logger.info("Game over!")
        elif not self.board.is_piece_active():
            self._score_and_clear_completed_lines()
            self._update_game_level()
            self._spawn_new_piece()

    def _spawn_new_piece(self):
        tetromino = self.piece_maker.get_random_shape()
        self.board.spawn_piece(tetromino)
        self._reset_clocks()

    def _redraw_pieces(self):
        self.blocks.clear()
        for (x, y), piece_id in self.board.get_blocks().items():
            x = x * self.block_size
            y = self.height - ((y + 1) * self.block_size)
            block_color = self.piece_maker.get_shape_from_id(piece_id).color
            self.blocks.append(
                Block(block_color, x=x, y=y, width=self.block_size, height=self.block_size, batch=self.batch))

    def _unschedule_clocks(self):
        pyglet.clock.unschedule(self.fall)

    def _schedule_clocks(self):
        pyglet.clock.schedule_interval(self.fall, self.gravity)
        pyglet.clock.schedule_interval(self.move, self.MOVE_SPEED_IN_SECONDS)

    # noinspection PyAttributeOutsideInit
    def reset(self):
        self.board = Board(self.width // self.block_size,
                           self.height // self.block_size,
                           print_board=self._print_to_console)
        self.blocks.clear()
        self.piece_maker.reset()
        self._paused = False
        self._toggle_game_paused_text(False)
        self._score = 0
        self._score_label.text = f'Score: 0'
        self._level = 1
        self._gravity_bps = 0.7  # seconds per block
        self.game_over = False
        self._cleared_lines = 0
        self._spawn_new_piece()
        self._unschedule_clocks()
        self._schedule_clocks()

    @property
    def gravity(self):
        return self._gravity_bps

    @property
    def level(self):
        return self._level

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score
        self._score_label.text = f'Score: {self._score}'
        _logger.info(f"New score: {self._score}")

    def pause(self, show_text=True):
        if not self._paused:
            _logger.info("Game paused")
            self._paused = True
            self._toggle_game_paused_text(show_text)
            self._unschedule_clocks()
        else:
            _logger.info("Game unpaused")
            self._paused = False
            self._toggle_game_paused_text(False)
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
            self._cleared_lines += full_rows

    def _toggle_game_paused_text(self, toggle):
        if toggle:
            self._game_paused_text = pyglet.text.Label(
                f'Paused',
                font_name='Times New Roman',
                font_size=18,
                x=self.width // 2, y=self.height // 2, anchor_x='center', anchor_y='center',
                batch=self._text_batch)
            self._game_paused_text.set_style('background_color', (0, 0, 0, 255))
        elif self._game_paused_text:
            self._game_paused_text.delete()

    def _update_game_level(self):
        if self._cleared_lines >= self.LINES_PER_LEVEL and self._level < self.MAX_LEVEL:
            self._cleared_lines -= self.LINES_PER_LEVEL
            self._gravity_bps *= 0.8
            self._level += 1
            new_level_text = pyglet.text.Label(
                f'Level {self._level}',
                font_name='Times New Roman',
                font_size=18,
                x=self.width // 2, y=self.height - (self.height // 4), anchor_x='center', anchor_y='center',
                batch=self._text_batch)
            new_level_text.set_style('background_color', (0, 0, 0, 255))
            pyglet.clock.schedule_once(lambda dt: new_level_text.delete(), 2)

    def level_up(self):
        self._cleared_lines = self.LINES_PER_LEVEL
        self._update_game_level()
