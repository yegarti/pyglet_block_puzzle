class BoardPrinter:

    def __init__(self, board, width, height):
        self._board = board
        self._width = width
        self._height = height

    def print_to_console(self):
        for j in range(self._height):
            for i in range(self._width):
                if j == 0 and i == 0:
                    self._print_board_top_header()
                if i == 0:
                    self._print_board_wall()

                cell = self._board[i][j]
                print(f"{cell}", end='')

                if i == self._width - 1:
                    self._print_board_wall()

            print()
        self._print_board_horizontal_header()
        print()

    def _print_board_horizontal_header(self):
        for _ in range(self._width):
            print("-", end='')

    def _print_board_wall(self):
        print('|', end='')

    def _print_board_top_header(self):
        print()
        print("Board")
        self._print_board_horizontal_header()
        print()
