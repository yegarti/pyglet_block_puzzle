import pytest

from pyglet_tetris.board import Board, BoardBlock, BoardPiece
from pyglet_tetris.shape import Straight


@pytest.fixture()
def board():
    return Board(10, 10)


@pytest.fixture()
def block():
    return BoardBlock(0, 0)


@pytest.fixture()
def straight_piece() -> BoardPiece:
    blocks = [BoardBlock(x, 0) for x in range(4)]
    center = BoardBlock(Straight.center[0], Straight.center[1])
    return BoardPiece(Straight(), blocks, center)


def test_board_new(board):
    assert board.get_blocks() == {}


def test_board_spawn_piece(board):
    assert not board.is_piece_active()
    board.spawn_piece(Straight)
    assert board.is_piece_active()
    assert board.get_blocks() != {}


def test_board_drop(board):
    old_blocks = board.get_blocks()
    board.spawn_piece(Straight)
    board.drop()
    assert board.get_blocks() != old_blocks


def test_board_move(board):
    old_blocks = board.get_blocks()
    board.spawn_piece(Straight)
    board.move_right()
    assert board.get_blocks() != old_blocks


def test_board_game_over(board):
    assert not board.is_game_over()
    board.spawn_piece(Straight)
    board.spawn_piece(Straight)
    assert board.is_game_over()


def test_board_rotate(board):
    board.spawn_piece(Straight)
    old_blocks = board.get_blocks()
    board.rotate()
    # blocked by top border
    assert old_blocks == board.get_blocks()

    for _ in range(5):
        board.drop()
    board.rotate()
    assert old_blocks != board.get_blocks()


def test_board_limit_movement(board):
    board.spawn_piece(Straight)
    for _ in range(20):
        board.move_left()
    old_blocks = board.get_blocks()
    board.move_left()
    assert old_blocks == board.get_blocks()


def test_block_init(block):
    assert (block.x, block.y) == (0, 0)


def test_block_add(block):
    b = block + BoardBlock(1, 2)
    assert (b.x, b.y) == (1, 2)
    b += BoardBlock(-1, 2)
    assert (b.x, b.y) == (0, 4)


def test_piece_init(straight_piece: BoardPiece):
    assert straight_piece.center == BoardBlock(Straight.center[0], Straight.center[1])
    assert straight_piece.blocks == [BoardBlock(x, 0) for x in range(4)]
    assert straight_piece.id == Straight().id


def test_piece_move(straight_piece: BoardPiece):
    old_blocks = straight_piece.blocks
    old_center = straight_piece.center
    straight_piece.move(1, 2)
    for old in old_blocks:
        assert old + BoardBlock(1, 2) in straight_piece.blocks
    assert straight_piece.center == old_center + BoardBlock(1, 2)


def test_piece_rotate(straight_piece: BoardPiece):
    straight_piece.move(4, 5)
    old_center = straight_piece.center
    straight_piece.rotate()
    assert straight_piece.center == old_center
    # assert all 'x' are the same after rotation
    assert len(set(map(lambda block: block.x, straight_piece.blocks))) == 1
