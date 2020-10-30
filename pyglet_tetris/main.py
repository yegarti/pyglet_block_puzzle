import logging

import pyglet

from pyglet_tetris.game import Game

DEBUG = False

_logger = logging.getLogger()
logging.basicConfig()
_logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

WIDTH = 250
HEIGHT = 500
BLOCK_SIZE = WIDTH // 10


class Tetris(pyglet.window.Window):
    def __init__(self, width, height, block_size):
        super().__init__(
            caption='Tetris',
            width=width,
            height=height,
            fullscreen=False,
            resizable=False
        )
        self.main_batch = pyglet.graphics.Batch()
        self.text_batch = pyglet.graphics.Batch()
        self.game = Game(width, height, block_size,
                         self.main_batch,
                         self.text_batch,
                         print_to_console=DEBUG)
        self.push_handlers(self.game.key_handler)
        self.push_handlers(self.game)
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)

    def update(self, dt):
        if self.game.game_over:
            if not self.game.is_paused():
                self.game.pause(show_text=False)
                print('Game Over!')
        else:
            self.game.update(dt)

    def on_draw(self):
        self.clear()
        self.main_batch.draw()
        self.text_batch.draw()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol == pyglet.window.key.R:
            self.game.reset()
        if symbol == pyglet.window.key.P:
            self.game.pause()
        if symbol == pyglet.window.key.L:
            self.game.level_up()


if __name__ == '__main__':
    game = Tetris(WIDTH, HEIGHT, BLOCK_SIZE)
    pyglet.app.run()
