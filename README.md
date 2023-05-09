# Tic-Tac-Toe AI

This is a simple little game playing "AI" that can play Tic-Tac-Toe (Noughts
and crosses). There are several versions, written in Python, Rust, Java and C++. You
may play against either in a simple command line interface. You will never win,
however, as the AI never plays a move allowing you to do so.

This project was made as a simple demo of game playing computer programs,
illustrating an implementation of the [minimax algorithm](https://en.wikipedia.org/wiki/Minimax).

In addition, an implementation of [Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
can be found in [mcts.py](mcts.py), showcasing a quite different approach.

## Run (Python)
To play against the [Python version](tictactoe.py) of the AI, simply run the
program in a terminal. The script allows you to chose the players, and you can
even have different AIs play each other.

Below is a short demo:
```
> python3 play.py
Who is player 1?
	 (1) You (human)
	 (2) MiniMax (AI)
	 (3) MCTS with random rollout (AI)
	 (3) MCTS with perfect rollout (AI)

Enter choice: 1

Who is player 2?
	 (1) You (human)
	 (2) MiniMax (AI)
	 (3) MCTS with random rollout (AI)
	 (3) MCTS with perfect rollout (AI)

Enter choice: 2

-|-|-
-----
-|-|-
-----
-|-|-

Enter move (1-9): 5
-|-|-
-----
-|X|-
-----
-|-|-

-|-|-
-----
-|X|-
-----
-|-|O

Enter move (1-9):
```

## Run (Rust)
To play against the [Rust version](tictactoe.rs) of the AI, you can use the provided [Makefile](Makefile):
```
> make run-rust
Best move found in an average of 0.28ms

---+---+---
   |   |
---+---+---
   |   |
---+---+---
   |   |
---+---+---

Enter move [0, 9):
```

## Run (C++)
To play against the [C++ version](tictactoe.cpp) of the AI, you can use the provided [Makefile](Makefile). This
implementation uses a [Bitboard](https://en.wikipedia.org/wiki/Bitboard) representation of the game, for variety. In
the case of Tic-Tac-Toe, it's slower than a simple array, but in games like chess they are essential.
``` 
> make run-cpp
Guaranteed outcome with optimal play (1 = Cross, -1 = nought, 0 = draw): 0
Found in average time out of 100 times: 0.90 ms 
Don't trust the AI's determination? Go ahead, try to beat it. You can even go first.

-|-|-
-----
-|-|-
-----
-|-|-
Your move:
```

## Run (Java)
To play against the [Java version](tictactoe.java) of the AI, you can also use the provided [Makefile](Makefile):
```
> make run-java
Found best move in 1.00 ms on average of 100 times.

-|-|-
-|-|-
-|-|-

Your move: 
```
