#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monte Carlo Tree Search (MCTS) implementation for Tic-Tac-Toe.

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

from tictactoe import Board, CROSS, NOUGHT, search
import time
import random
import abc
from itertools import count
from math import sqrt, log


class RolloutPolicy(abc.ABC):
    """A callable that assigns a score to board states."""

    @abc.abstractmethod
    def __call__(self, board):
        """Return an evaluation for the board. Must correctly handle decided boards."""
        pass


class RandomRollout(RolloutPolicy):
    """Rollout games based on random moves."""

    def __call__(self, board):
        while not board.is_decided:
            board = board.do_move(random.choice(list(board.moves())))
        return board.score


class PerfectRollout(RolloutPolicy):
    """Decide outcome by perfect search."""

    def __call__(self, board):
        return search(board)[0]


class Node(object):
    """
    A node in the MctsTree.

    This class should not be used outside MctsTree, and therefore the
    documentation is limited to explanations of methods, rather than
    documenting arguments and returns.

    Of note is simply the attributes stored in the constructor.
    """

    def __init__(self, board, parent=None):
        self.board = board
        self.parent = parent

        self.N = 0  # Visit count.
        self.W = 0  # Total score.
        self.children = []

    @property
    def is_leaf(self):
        return self.board.is_decided

    @property
    def has_children(self):
        return bool(self.children)

    @property
    def can_be_expanded(self):
        return not self.has_children and not self.is_leaf

    def expand(self):
        assert self.can_be_expanded
        self.children = [
            Node(self.board.do_move(move), parent=self) for move in self.board.moves()
        ]

    def rollout_and_update(self, rollout_policy):
        """
        Assign W/L/D score to every child node and update statistics.

        This will propagate the update up to all parent nodes.

        The rollout policy defines some strategy for assigning a score to the board.
        """
        paths = self.children
        # In case of a leaf node, we just evaluate on our self, as there are no children.
        if self.is_leaf:
            paths = [self]
        for path in paths:
            outcome = rollout_policy(path.board)
            path.update_stats(outcome)

    def update_stats(self, outcome):
        """
        Update stats with the new outcome, and propagate upwards.

        Note that we send the negated outcome to the parent, as they have the
        opposite perspective.
        """
        self.W += outcome
        self.N += 1
        if self.parent:
            self.parent.update_stats(-outcome)

    def uct_inverted(self, control_parameter=0):
        """
        Compute the negated UCT score.

        This assigns a large value if this node is desirable from
        the parents point of view. Depending on the control parameter,
        we might assign this node a high score even if it is undesirable
        for the parent, if it has not been explored enough.
        """
        return -self.W / self.N + control_parameter * sqrt(log(self.parent.N) / self.N)

    def max_uct_child(self, control_parameter=0):
        """Return the child node with maximum UCT score."""
        assert not self.can_be_expanded
        if self.is_leaf:
            return self
        return max(
            self.children, key=lambda child: child.uct_inverted(control_parameter)
        )

    def __str__(self):
        return "{}\nW/N = {:.2f}, N = {}".format(
            str(self.board), self.W / self.N, self.N
        )

    def child_str(self):
        """Print children. Do not look at this. Seriously. It doesn't even work properly."""
        c = [str(child).split("\n") for child in self.children]
        col_len = len(max(c, key=lambda b: max(b))) + 4
        return "\n".join(
            (
                " "
                * (
                    (i != len(list(zip(*c))) - 1) * col_len
                    + ((i == len(list(zip(*c))) - 1)) * 3
                )
            ).join(rows)
            for i, rows in enumerate(list(zip(*c)))
        )


class MctsTree(object):
    """A Monte Carlo Search Tree."""

    def __init__(self, board, rollout_policy=RandomRollout()):
        """
        Define a new search tree starting at the given position.

        Arguments
        ---------
        board: tictactoe.Board
            A game object defining the board to search, see tictactoe.Board
        rollout_policy: RolloutPolicy, optional
            Define the policy to use to assign scores to board states. Default is RandomRollout.
        """
        self.root = Node(board)
        self.rollout_policy = rollout_policy

    def search(
        self, secs, control_parameter=lambda *args: 1, terminate=lambda *args: False
    ):
        """
        Perform a Monte Carlo Tree search from the root position.

        Arguments
        ---------
        secs: float
            How many seconds to search for. Can be `float('inf')` if search is bounded by
            the terminate function.
        control_parameter: f(t0, it) -> number, optional
            A function of the starting time and the number of iterations that have run,
            which returns the exploration control parameter to use for the next iteration.
            Default is to always return 1.
            Example: lambda t0, it: 0.99**it gives a decaying value.
        terminate: f(t0, it) -> bool
            A function of the starting time and the number of iterations that have run,
            which returns True if the search should stop.
            Example: lambda t0, it: it >= 1000 will stop after 1000 iterations.

        Returns
        -------
            The search node corresponding to the best available move, as determined by the search.
            Of note, `node.board` gives the game state it self, but other statistics are also
            available through the node object.
        """
        t0 = time.time()

        for iteration in count(1):
            self._mct_expand(control_parameter(t0, iteration))
            if time.time() - t0 > secs or terminate(t0, iteration):
                break

        return max(self.root.children, key=lambda child: child.N)

    def _mct_expand(self, control_parameter=0):
        """Perform one iteration of MCTS."""

        # Traverse down the tree, picking nodes according to UCT scores.
        node = self.root
        while node.has_children:
            node = node.max_uct_child(control_parameter)

        # At this point we either have a leaf node or an unexpanded node.
        # In case of the latter we expand its children.
        if node.can_be_expanded:
            node.expand()

        # Evaluate the score of the node, or the score of all the children,
        # and propagate updates back up the tree.
        node.rollout_and_update(self.rollout_policy)


if __name__ == "__main__":
    random.seed(2018)
    b = Board().do_move(16).do_move(1).do_move(256).do_move(64)
    tree = MctsTree(b, rollout_policy=RandomRollout())

    n = tree.search(
        secs=float("inf"),
        control_parameter=lambda t0, it: 1 ** (it),
        terminate=lambda t0, it: it > 10000,
    )
    print(tree.root)
    print()
    print(tree.root.child_str())

    print(n)
    print()
    print(n.child_str())
