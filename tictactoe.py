#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import math

CROSS, NOUGHT = 0, 1
PLAYERS = [CROSS, NOUGHT]

# Winning patterns encoded in bit patterns.
# E.g. three in a row in the top row is
#   448 = 0b111000000
WINNING_PATTERNS = [448, 56, 7,    # Row
                    292, 146, 73,  # Columns
                    273, 84]       # Diagonals


class Board(object):
    """
    Representation of a Tic-tac-toe game.
    Board represented by two bitboards, one for each player,
    where a set bit indicates that the given player has played a
    move on the corresponding square.

    Example:

        X|O|X
        -+-+-          CROSS        NOUGHT
        O|X|O   = [ 0b101010101, 0b010101010 ]
        -+-+-
        X|O|X
    """

    def __init__(self, squares=(0, 0), turn=CROSS, depth=0):
        self.squares = list(squares)  # First is X-board, second O-board.
        self.turn = turn
        self.depth = depth

    @property
    def score(self):
        """Return +1 if self.turn has won, -1 for loss and 0 otherwise."""
        for player in PLAYERS:
            for pattern in WINNING_PATTERNS:
                if (self.squares[player] & pattern) == pattern:
                    return 1 if player == self.turn else -1
        return 0

    @property
    def is_decided_and_score(self):
        """Return (b, s) where b is True if the game is over, and s is the score."""
        score = self.score
        return bool(score) or self.depth == 9, score

    @property
    def is_decided(self):
        """Return True if the game is over."""
        return self.depth == 9 or bool(self.score)

    def next_player(self):
        return CROSS if self.turn == NOUGHT else NOUGHT

    def moves(self):
        """Generator for all possible moves."""
        # Every non-occupied square is a move.
        taken = self.squares[CROSS] | self.squares[NOUGHT]
        square = 256  # Bottom right corner.
        while square:
            if not (taken & square):
                yield square
            square = square >> 1

    def do_move(self, move):
        """Return a board where the suggested move has been made."""
        b = Board(squares=self.squares[:],  # Copy squares.
                  turn=self.next_player(),  # Swap player to move.
                  depth=self.depth + 1)     # Increment depth.
        b.squares[self.turn] |= move        # Apply move.
        return b

    def __repr__(self):
        """Return string representation of the board."""
        s = ''
        for i in range(9):
            if self.squares[CROSS] & (1 << i):
                s += 'X'
            elif self.squares[NOUGHT] & (1 << i):
                s += 'O'
            else:
                s += '-'
            if i % 3 < 2:
                s += '|'
            elif i < 8:
                s += '\n-----\n'
        return s


def search(board, lower=-1, upper=1):
    """
    Return score and best move, relative to board.turn.

    The search is an implementation of a depth-unlimited
    Negamax-algorithm, a variant of Minimax.
    """

    # If game is over we know the score.
    decided, score = board.is_decided_and_score
    if decided:
        return score, None

    # Recursively explore the available moves, keeping
    # track of the best score and move to play.
    bestScore, bestMove = -float('inf'), None

    for move in board.moves():

        # v is score of position after the move.
        v = - search(board.do_move(move), -upper, -lower)[0]

        # New best move?
        if v > bestScore:
            bestScore = v
            bestMove = move

        # Update lower bound. Guaranteed at least a score of max(lower, v).
        lower = max(lower, v)

        # Pruning: If lower bound equals the upper bound, the true score
        # must be the currently best score. No need to explore other branches.
        if lower >= upper:
            break

    return bestScore, bestMove


def play():
    "Play against the AI in a simple text interface."
    import re
    board = Board()
    while True:
        print()
        print(board)

        decided, _ = board.is_decided_and_score
        if decided:
            print("You lost")
            if input("Play again? (y/n) ") == 'y':
                play()
            break

        # We query the user until she enters a legal move.
        move = None
        while move not in board.moves():
            match = re.match('[1-9]', input('Your move: '))
            if match:
                move = 2 ** (int(match.string[0]) - 1)
            else:
                # Inform the user when invalid input (e.g. "help") is entered
                print("Please enter a move like 3 for top right.")
        board = board.do_move(move)

        print()
        print(board)

        decided, score = board.is_decided_and_score
        if decided and score == 0:
            print("It's a draw")
            if input("Play again? (y/n) ") == 'y':
                play()
            break

        score, move = search(board)

        print('My move: {}'.format(round(math.log2(move) + 1)))
        board = board.do_move(move)


if __name__ == "__main__":
    play()
