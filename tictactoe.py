"""
Simple Tic-Tac-Toe game playing AI.

MIT License
Copyright 2018 Bendik Samseth

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from collections import namedtuple

CROSS  = 'X'
NOUGHT = 'O'
CROSSES_WIN = [t for t in CROSS * 3]
NOUGHTS_WIN = [t for t in NOUGHT * 3]

Move = namedtuple('Move', ['row', 'col', 'type'])
Winning = namedtuple('Winning', ['type', 'move'])

class Board(object):
    def __init__(self):
        self.squares = [[' ', ' ', ' '],
                        [' ', ' ', ' '],
                        [' ', ' ', ' ']]
        self.turn = 'X'
        self.depth = 0

    def isDecided(self):
        "Return the winning type ('X', 'O', ' ') or None if game not completed."
        # Check rows.
        for row in self.squares:
            if row == CROSSES_WIN: return CROSS
            elif row == NOUGHTS_WIN: return NOUGHT
        # Check cols.
        for col in [list(i) for i in zip(*self.squares)]:
            if col == CROSSES_WIN: return CROSS
            elif col == NOUGHTS_WIN: return NOUGHT
        # Check diagonals.
        for diag in ([self.squares[0][0], self.squares[1][1], self.squares[2][2]],
                     [self.squares[0][2], self.squares[1][1], self.squares[2][0]]):
            if diag == CROSSES_WIN: return CROSS
            elif diag == NOUGHTS_WIN: return NOUGHT
        # No winner, might be draw?
        if self.depth == 9:
            return ' '
        # Not decided, return nothing.
        return None

    def moves(self):
        "Generator for all possible moves."
        # Every non-occupied square is a move.
        for i, row in enumerate(self.squares):
            for j, square in enumerate(row):
                if square == ' ':
                    yield Move(i, j, self.turn)

    def doMove(self, move):
        "Return a board where the suggested move has been made."
        # Make a copy board and change as needed.
        b = Board()
        b.squares = [row[:] for row in self.squares]
        b.squares[move.row][move.col] = move.type
        b.turn = CROSS if self.turn == NOUGHT else NOUGHT
        b.depth = self.depth + 1
        return b

    def __str__(self):
        return '\n------\n'.join('|' + '|'.join(row) + '|' for row in self.squares) + '\n'


def search(board):
    "Return a Winning(type, move) instance indicating the winning side and move to play."
    winner = board.isDecided()
    if winner:
        return Winning(winner, None)

    if board.turn == CROSS:
        best = Winning(NOUGHT, None)
        for move in board.moves():
            v = search(board.doMove(move))
            if v.type == CROSS:
                return Winning(CROSS, move)
            elif v.type == ' ':
                best = Winning(' ', move)
    else:
        best = Winning(CROSS, None)
        for move in board.moves():
            v = search(board.doMove(move))

            if v.type == NOUGHT:
                return Winning(NOUGHT, move)
            elif v.type == ' ':
                best = Winning(' ', move)
    return best


def play():
    "Play against the AI in a simple text interface."
    import re
    board = Board()
    while True:
        print()
        print(board)

        decided = board.isDecided()
        if decided == NOUGHT:
            print("You lost")
            if input("Play again? (y/n) ") == 'y':
                play()
            break

        # We query the user until she enters a (pseudo) legal move.
        move = None
        while move not in board.moves():
            match = re.match('[0-2]'*2, input('Your move: '))
            if match:
                move = Move(int(match.string[0]), int(match.string[1]), CROSS)
            else:
                # Inform the user when invalid input (e.g. "help") is entered
                print("Please enter a move like 02")
        board = board.doMove(move)

        print()
        print(board)

        decided = board.isDecided()
        if decided == CROSS:
            print("You won")
            if input("Play again? (y/n) ") == 'y':
                play()
            break
        elif decided == ' ':
            print("It's a draw")
            if input("Play again? (y/n) ") == 'y':
                play()
            break

        winning = search(board)

        print('My move: {}{}'.format(winning.move.row, winning.move.col))
        board = board.doMove(winning.move)


if __name__ == "__main__":
    play()

