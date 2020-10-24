import logging

import pyglet

from pyglet_tetris.config import GameConfig
from pyglet_tetris.game import Game


_logger = logging.getLogger()
logging.basicConfig()
_logger.setLevel(logging.DEBUG)

class Tetris(pyglet.window.Window):
    def __init__(self, game_config: GameConfig):
        super().__init__(
            caption='Tetris',
            width=game_config.width,
            height=game_config.height,
            fullscreen=game_config.full_screen,
            resizable=False
        )
        self.block_size = game_config.width // 10
        self.main_batch = pyglet.graphics.Batch()
        self.text_batch = pyglet.graphics.Batch()
        self.game = Game(game_config.width, game_config.height, self.block_size,
                         self.main_batch,
                         self.text_batch)
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
    config = GameConfig(load_saved_config=True)
    game = Tetris(config)
    pyglet.app.run()
