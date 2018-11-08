"""
This module defines a common interface for playing different AIs against humans
or other AIs.
"""
import random
import sys
import time
from abc import ABC, abstractmethod
from tictactoe import Board, search
from mcts import MctsTree, RandomRollout, PerfectRollout


class Player(ABC):
    """A player defines the interface needed to play a game.

    The only requirement is to be able to take a board and return
    a (legally) modified board.
    """

    @abstractmethod
    def make_move(self, board):
        pass


class HumanPlayer(Player):
    """Human controlled player."""

    def make_move(self, board):
        """Ask for a move until a legal one is given."""
        move = None
        while move not in board.moves():
            try:
                text = input("Enter move (1-9): ")
                move = 1 << int(text) - 1
            except:
                if text.lower().startswith("q"):
                    sys.exit(0)
                print("No! Enter a single number, 1-9")
        return board.do_move(move)


class PerfectPlayer(Player):
    """AI who always plays the best move."""

    def make_move(self, board):
        score, move = search(board)
        return board.do_move(move)


class MctsPlayer(Player):
    """
    Monte Carlo Tree Search based AI.

    Adjust strength by changing the amount of allowed iterations/thinking time,
    exploration control parameter and rollout policy.
    """

    def __init__(self, rollout_policy=RandomRollout()):
        self.rollout_policy = rollout_policy

    def make_move(self, board):
        """Pick the most preferred, legal move."""
        tree = MctsTree(board, rollout_policy=self.rollout_policy)
        new_pos = tree.search(
            secs=float("inf"),
            control_parameter=lambda t0, it: 0.999 ** (it),
            terminate=lambda t0, it: it > 5000,
        )
        return new_pos.board


def play(player1=HumanPlayer(), player2=MctsPlayer(), verbose=True):
    """Play a player vs. player in an infinite death match."""
    print_if = lambda *args, **kwargs: print(*args, **kwargs) if verbose else None
    scores = [0, 0]
    while True:
        b = Board()
        print_if(b, end="\n\n")
        i = random.randint(0, 1)  # Decide who starts.
        while not b.is_decided:
            player = player2 if i & 1 else player1
            b = player.make_move(b)
            print_if(b, end="\n\n")
            i += 1
        score = b.score
        if score and i & 1:
            scores[0] += 1
        elif score:
            scores[1] += 1
        else:
            scores[0] += 0.5
            scores[1] += 0.5
        print("\n\t\033[1mScore: {} - {}\033[0m\n".format(*scores))


if __name__ == "__main__":
    implemented_players = [
        HumanPlayer(),
        PerfectPlayer(),
        MctsPlayer(),
        MctsPlayer(PerfectRollout()),
    ]
    players = []
    try:
        for player in range(1, 3):
            print("Who is player {}?".format(player))
            print("\t (1) You (human)")
            print("\t (2) MiniMax (AI)")
            print("\t (3) MCTS with random rollout (AI)")
            print("\t (3) MCTS with perfect rollout (AI)")
            players.append(implemented_players[int(input("\nEnter choice: ")) - 1])
            print()
    except:
        print("To hard, huh?")
        sys.exit(1)

    play(*players)
