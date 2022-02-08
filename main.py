from enum import Enum
from typing import List, Tuple, Optional
import itertools
import random


class BoardBox(Enum):
    EMPTY = ' '
    WALL = 'X'
    PATH = '*'
    HOME = 'D'


class Figure:

    def __init__(self, start_position: Tuple[int, int], representation: str):
        self.start_position = start_position
        self.position = start_position
        self.representation = representation

    def __str__(self):
        return self.representation

    def next_position(self, board: 'Board', moves: int) -> Optional[Tuple[int, int]]:
        position = self.position

        for _ in range(moves):
            position = board.next_position(position[0], position[1])
            if position == self.start_position:
                position = board.home_position(position[0], position[1])
            if position is None:
                return None
        figure, _player = board.figure_at(position[0], position[1])
        if figure and board.box_at(position[0], position[1]) == BoardBox.HOME:
            return None
        return position

    def move_to(self, position: Tuple[int, int]):
        self.position = position

    def is_home(self, board: 'Board'):
        x, y = self.position
        return board.box_at(x, y) == BoardBox.HOME


class Player:

    def __init__(self, representation: str, home_position: Tuple[int, int]):
        self.representation = representation
        self.home_position = home_position
        self.figures: List[Figure] = []

    def add_figure(self):
        self.figures.append(Figure(self.home_position, self.representation))

    def figure_at(self, x: int, y: int) -> Optional[Figure]:
        for figure in self.figures:
            if figure.position == (x, y):
                return figure
        return None

    def figures_finished(self, board: 'Board') -> bool:
        for figure in self.figures:
            if not figure.is_home(board):
                return False
        return True

    def active_figures(self, board: 'Board') -> List[Figure]:
        return [figure for figure in self.figures if not figure.is_home(board) or figure.next_position(board, 1) is not None]

    def has_finished(self, board: 'Board') -> bool:
        return len(self.figures) == board.max_figures and self.figures_finished(board)

    def delete_figure(self, figure: Figure):
        self.figures.remove(figure)

    def __str__(self):
        return self.representation


class Board:

    def __init__(self, n):
        assert n % 2
        self.n = n
        self._build_board()
        self.players: List[Player] = []
        self.starts = [
            (n // 2 + 1, 0),
            (n // 2 - 1, n - 1),
        ]

    @property
    def max_figures(self):
        return (self.n - 3) // 2

    def figure_at(self, x, y) -> Tuple[Optional[Figure], Optional[Player]]:
        for player in self.players:
            figure = player.figure_at(x, y)
            if figure is not None:
                return figure, player
        return None, None

    def move_figure(self, figure: Figure, x: int, y: int):
        del_figure, del_player = self.figure_at(x, y)
        if del_figure is not None:
            del_player.delete_figure(del_figure)
        figure.move_to((x, y))
        return del_figure

    def add_player(self, representation=None) -> Player:
        if representation is None:
            representation = chr(len(self.players) + ord('A'))
        home_pos = self.starts[len(self.players)]
        player = Player(representation, home_pos)
        player.add_figure()
        self.players.append(player)
        return player

    def next_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        m = self.n // 2
        posible_moves = []
        if x == m:
            if y < m - 1 and y != 0:
                return x, y + 1
            if y > m + 1 and y != self.n - 1:
                return x, y - 1
        if y == m:
            if x < m - 1 and x != 0:
                return x + 1, y
            if y > m + 1 and y != self.n - 1:
                return x - 1, y
        if self.board[x][y] == BoardBox.HOME:
            return None

        if x < m:
            if y > 0:
                posible_moves.append((x, y - 1))
        elif y < self.n - 1:
            posible_moves.append((x, y + 1))

        if y < m:
            if x < self.n - 1:
                posible_moves.append((x + 1, y))
        elif x > 0:
            posible_moves.append((x - 1, y))

        for px, py in posible_moves:
            if self.board[py][px] == BoardBox.PATH:
                return px, py

        return None

    def home_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        m = self.n // 2
        if x == 0:
            return 1, m
        if x == self.n - 1:
            return self.n - 2, m
        if y == 0:
            return m, 1
        if y == self.n - 1:
            return m, self.n - 2
        return None

    def box_at(self, x: int, y: int):
        m = self.n // 2
        if x == m or y == m:
            if x == y:
                return BoardBox.WALL
            if x in (0, self.n - 1) or y in (0, self.n - 1):
                return BoardBox.PATH
            return BoardBox.HOME
        if (x < m - 1 or x > m + 1) and (y < m - 1 or y > m + 1):
            return BoardBox.EMPTY
        return BoardBox.PATH

    def _build_board(self):
        self.board = [
            [
                self.box_at(x, y)
                for x in range(self.n)
            ] for y in range(self.n)
        ]

    def print(self):
        print(' ', end='')
        for x in range(self.n):
            print(f' {x % 10}', end='')
        print()

        for y in range(self.n):
            print(y % 10, end='')
            for x in range(self.n):
                figure, _player = self.figure_at(x, y)
                if figure is None:
                    print(f' {self.board[y][x].value}', end='')
                else:
                    print(f' {figure}', end='')
            print()


def gensachovnicu(n: int) -> Board:
    return Board(n)


def tlacsachovnicu(board: Board) -> None:
    board.print()


def simulacia(n):
    board = gensachovnicu(n)
    board.add_player('A')
    board.add_player('B')
    board.print()
    for player in itertools.cycle(board.players):
        dice = random.randint(1, 6)
        print(f'Hrac {player} hodil {dice}')
        active_figures = player.active_figures(board)
        if not active_figures:
            if dice == 6 and len(player.figures) < board.max_figures:
                player.add_figure()
                print(f'Hrac {player} pridal figurku na hraciu plochu')
            else:
                print(f'Hrac {player} vynechava tah, pretoze nema aktivnu figurku mimo domceku')
        else:
            figure = active_figures[0]
            next_move = figure.next_position(board, dice)
            if next_move is not None:
                deleted_figure = board.move_figure(figure, next_move[0], next_move[1])
                print(f'Hrac {player} sa posunul o {dice}')
                if deleted_figure is not None:
                   print(f'Hrac {player} vyhodil figurku {deleted_figure}')
            else:
                print(f'Hrac {player} vynechava tah, pretoze sa nemoze pohnut o {dice}')

        board.print()
        print('-----------------------')
        if player.has_finished(board):
            print(f'Hrac {player} vyhral hru')
            break


if __name__ == '__main__':
    n = int(input('Zadaj velkost hracej plochy (Neparne cislo > 3): '))
    simulacia(n)
