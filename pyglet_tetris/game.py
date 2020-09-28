import random
import typing
import time

import pyglet
from pyglet.window import key

from pyglet_tetris.shape import ShapeMaker, Tetromino


class Game:

    MOVE_DELTA = 0.2

    def __init__(self, width, height, block_size, batch):
        self.width = width
        self.height = height
        self.block_size = block_size
        self.piece_maker = ShapeMaker(block_size, batch)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.fall_speed = 0.2
        self.move_speed = 0.1
        self.reset()
        self.latest_move = time.time()
        self._paused = False

    def update(self, dt):
        if not self._active_piece:
            self._spawn_new_piece()

    def _spawn_new_piece(self):
        piece_shape = random.choice(list(Tetromino))
        self._active_piece = self.piece_maker.new(self.width // 2 - self.block_size, self.height, piece_shape)

    def _unschedule_clocks(self):
        pyglet.clock.unschedule(self.fall)
        pyglet.clock.unschedule(self.move)

    def _schedule_clocks(self):
        pyglet.clock.schedule_interval(self.fall, self.fall_speed)
        pyglet.clock.schedule_interval(self.move, self.move_speed)

    # noinspection PyAttributeOutsideInit
    def reset(self):
        self.board = [[0] * self.width] * self.height
        self._paused = False
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

    def on_key_press(self, symbol, modifiers):
        if self._paused:
            return
        if symbol == key.RIGHT:
            self._active_piece.x += self.block_size
        if symbol == key.LEFT:
            self._active_piece.x -= self.block_size
        if symbol == key.UP:
            self._active_piece.rotate()
        self.latest_move = time.time()

    def move(self, dt):
        if self._paused:
            return
        if time.time() - self.latest_move < Game.MOVE_DELTA:
            return
        if self.key_handler[pyglet.window.key.RIGHT]:
            self._active_piece.x += self.block_size
        if self.key_handler[pyglet.window.key.LEFT]:
            self._active_piece.x -= self.block_size

    def fall(self, dt):
        self._active_piece.y -= self.block_size