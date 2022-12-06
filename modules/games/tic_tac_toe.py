import random
from typing import Literal, get_args


class TicTacToeCell:
    def __init__(
        self, x_coord: int, y_coord: int, mark: Literal["cross", "zero"] = None
    ):
        self.x = x_coord
        self.y = y_coord
        self.mark = mark

    def coords(self) -> list[int, int]:
        return [self.x, self.y]


class TicTacToeField:
    def __init__(self, rows: int = 3, cols: int = 3, moves_to_win: int = 3):
        self.rows: int = rows
        self.cols: int = cols
        self.last_move: TicTacToeCell = TicTacToeCell(-1, -1)
        if moves_to_win > rows and moves_to_win > cols:
            raise AttributeError("Wrong arguments, win is impossible")
        self.moves_to_win = moves_to_win
        self.cells = [TicTacToeCell(j, i) for j in range(rows) for i in range(cols)]

    def get_cell_pos(self, cell: TicTacToeCell) -> int:
        return cell.x * self.cols + cell.y

    def is_empty(self) -> bool:
        for cell in self.cells:
            if cell.mark is not None:
                return False
        return True

    def is_full(self) -> bool:
        for cell in self.cells:
            if cell.mark is None:
                return False
        return True

    def move_is_possible(self, move: TicTacToeCell) -> bool:
        return self.cells[self.get_cell_pos(move)].mark is None

    def get_available_moves(self) -> list[TicTacToeCell]:
        return [cell for cell in self.cells if cell.mark is None]

    def add_move(self, cell: TicTacToeCell) -> bool:
        if self.move_is_possible(cell):
            self.last_move = cell
            self.cells[self.get_cell_pos(cell)] = cell
            return True
        return False

    def find_all_moves_by_mark(
        self, mark: Literal["cross", "zero"]
    ) -> list[TicTacToeCell]:
        return [cell for cell in self.cells if cell.mark == mark]

    def is_game_finished(self) -> list[TicTacToeCell]:
        x, y = self.last_move.x, self.last_move.y
        max_diff = self.moves_to_win

        left_board = max(0, y - max_diff)
        right_board = min(self.cols, y + max_diff)
        up_board = max(0, x - max_diff)
        down_board = min(self.rows, x + max_diff)

        mark = self.last_move.mark
        res = []
        for i in range(left_board, right_board):
            if self.cells[x * self.cols + i].mark == mark:
                res.append(self.cells[x * self.cols + i])
            else:
                res = []
            if len(res) == self.moves_to_win:
                return res

        for i in range(up_board, down_board):
            if self.cells[i * self.cols + y].mark == mark:
                res.append(self.cells[i * self.cols + y])
            else:
                res = []
            if len(res) == self.moves_to_win:
                return res

        if (
            right_board - y + x - up_board >= self.moves_to_win - 1
            and y - left_board + down_board - x >= self.moves_to_win - 1
        ):
            for i in range(
                -min(y - left_board, x - up_board), min(right_board - y, down_board - x)
            ):
                if self.cells[(x + i) * self.rows + y + i].mark == mark:
                    res.append(self.cells[(x + i) * self.rows + y + i])
                else:
                    res = []
                if len(res) == self.moves_to_win:
                    return res

        if (
            y - left_board + x - up_board >= self.moves_to_win - 1
            and right_board - y + down_board - x >= self.moves_to_win - 1
        ):
            for i in range(
                -min(right_board - y, x - up_board), min(y - left_board, down_board - x)
            ):
                if self.cells[(x + i) * self.rows + y - i].mark == mark:
                    res.append(self.cells[(x + i) * self.rows + y - i])
                else:
                    res = []
                if len(res) == self.moves_to_win:
                    return res
        return res

    def show(self):
        for cell in self.cells:
            if cell.y == 0:
                print("|", end="")
            if cell.mark is None:
                print("_", end="|")
            elif cell.mark == "cross":
                print("x", end="|")
            else:
                print("O", end="|")
            if cell.y == self.cols - 1:
                print()


class TicTacToePlayer:
    def __init__(self, mark: Literal["cross", "zero"], field: TicTacToeField):
        self.cells = []
        self.mark = mark
        self.field = field

    def move(self):
        x = int(input("enter x: "))
        y = int(input("enter y: "))
        move = TicTacToeCell(x, y, mark=self.mark)
        while not self.field.add_move(cell=move):
            # send message
            x = int(input())
            y = int(input())
            move = TicTacToeCell(x, y, mark=self.mark)
        self.cells.append(move)


class TicTacToeBot(TicTacToePlayer):
    def __init__(
        self,
        difficulty: Literal["easy", "normal", "hard"],
        mark: Literal["cross", "zero"],
        field: TicTacToeField,
    ):
        super().__init__(mark, field)
        self.difficult = difficulty

    # only for 3 x 3 field
    def find_win_move(self, mark_to_search: Literal["cross", "move"]):
        combinations = [
            [[0, 0], [0, 1], [0, 2]],
            [[1, 0], [1, 1], [1, 2]],
            [[2, 0], [2, 1], [2, 2]],
            [[0, 0], [1, 0], [2, 0]],
            [[0, 1], [1, 1], [2, 1]],
            [[0, 2], [1, 2], [2, 2]],
            [[0, 0], [1, 1], [2, 2]],
            [[0, 2], [1, 1], [2, 0]],
        ]

        other_player_mark = [
            mark
            for mark in get_args(Literal["cross", "zero"])
            if mark != mark_to_search
        ][0]
        unavailable_cells = self.field.find_all_moves_by_mark(other_player_mark)
        res = []
        for combo in combinations:
            is_added = True
            for unavailable_cell in unavailable_cells:
                if unavailable_cell.coords() in combo:
                    is_added = False
                    break
            if is_added:
                res.append(combo)
        combinations = res

        player_cells_coords = [
            cell.coords()
            for cell in self.field.find_all_moves_by_mark(mark=mark_to_search)
        ]
        res = []
        for combo in combinations:
            count = 0
            for coords in player_cells_coords:
                if coords in combo:
                    count += 1
            if count == 2:
                res.append(combo)
        combinations = res

        if len(combinations) == 0:
            return None

        move: list = random.choice(combinations)
        for cell in self.field.find_all_moves_by_mark(mark=mark_to_search):
            try:
                coords = cell.coords()
                pos = move.index(coords)
            except ValueError:
                continue
            if cell.coords() in move:
                move.pop(pos)
        x, y = move[0]
        return TicTacToeCell(x, y, mark=self.mark)

    def __private_get_random_move(self) -> TicTacToeCell:
        possible_moves = self.field.get_available_moves()
        move: TicTacToeCell = random.choice(possible_moves)
        return TicTacToeCell(move.x, move.y, mark=self.mark)

    # only for 3 x 3 field
    def __private_get_smart_move(self) -> TicTacToeCell:
        if len(self.cells) <= 1:
            if self.field.cells[4].mark is None:
                return TicTacToeCell(1, 1, self.mark)
            else:
                available_cells = []
                for cell in self.field.get_available_moves():
                    if (
                        cell.coords() in [[0, 0], [0, 2], [2, 0], [2, 2]]
                        and cell.mark is None
                    ):
                        available_cells.append(cell.coords())
                x, y = random.choice(available_cells)
                return TicTacToeCell(x, y, mark=self.mark)

    def move(self):
        # if bot can win - wins
        move = self.find_win_move(self.mark)
        if move is not None:
            pass
        # random
        elif self.difficult == "easy":
            move = self.__private_get_random_move()
        else:
            arg1, arg2 = get_args(Literal["cross", "zero"])
            mark = arg1 if arg2 == self.mark else arg2
            other_player_win_move = self.find_win_move(mark_to_search=mark)
            if other_player_win_move:
                move = other_player_win_move
            elif self.difficult == "normal":
                move = self.__private_get_random_move()
            else:
                move = self.__private_get_smart_move()
        self.cells.append(move)
        self.field.add_move(cell=move)


class TicTacToeGame:
    def __init__(
        self,
        player_1: TicTacToePlayer | TicTacToeBot,
        player_2: TicTacToePlayer | TicTacToeBot,
        field: TicTacToeField,
    ):
        self.player_1 = player_1
        self.player_2 = player_2
        self.field = field
        self.is_player_1_move = True

    def start_game(self) -> TicTacToePlayer | TicTacToeBot:
        while not self.field.is_full():
            # if player do move - await for his turn
            if self.is_player_1_move:
                self.player_1.move()
            else:
                self.player_2.move()
            # self.field.show()
            if len(self.field.is_game_finished()) == self.field.moves_to_win:
                if self.is_player_1_move:
                    return self.player_1
                else:
                    return self.player_2
            self.is_player_1_move = not self.is_player_1_move
        # self.field.show()


# field_ = TicTacToeField()
# player1 = TicTacToePlayer(mark="cross", field=field_)
# player2 = TicTacToeBot(mark="zero", field=field_, difficulty="hard")
# game = TicTacToeGame(player_1=player1, player_2=player2, field=field_)
#
# game.start_game()
