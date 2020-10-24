import pyglet
import pytest

from pyglet_tetris.game import Game


@pytest.fixture()
def game():
    return Game(200, 100, 10, None, None)


def test_game_init(game: Game):
    assert not game.game_over
    assert not game.is_paused()


def test_game_pause(game: Game):
    game.pause()
    assert game.is_paused()
    game.pause()
    assert not game.is_paused()


@pytest.mark.skip("Fail with 'Square' shape")
def test_key_rotate(game: Game):
    game.board.drop()
    game.board.drop()
    game.board.drop()
    blocks = game.board.get_blocks()

    game.on_key_press(pyglet.window.key.UP, None)

    assert game.board.get_blocks() != blocks


def test_key_full_drop(game: Game):
    blocks = game.board.get_blocks()
    game.on_key_press(pyglet.window.key.SPACE, None)
    assert game.board.get_blocks() != blocks
    assert not game.board.is_piece_active()


def test_score_hard_drop(game: Game):
    game.on_key_press(pyglet.window.key.SPACE, None)
    assert 0 < game.score <= game.height * 2


def test_score_soft_drop(game: Game):
    for _ in range(5):
        game.soft_drop()
    assert 0 < game.score <= 5
