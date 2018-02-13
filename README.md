# Tic-Tac-Toe AI

This is a simple little game playing "AI" that can play Tic-Tac-Toe (Noughts
and crosses). There are two versions, one written in Python and one in C++. You
may play against either in a simple command line interface. You will never win,
however, as the AI never plays a move allowing you to do so.

This project was made as a simple demo of game playing computer programs,
illustrating an implementation of the [minimax algorithm](https://en.wikipedia.org/wiki/Minimax).


## Run (Python)
To play against the [Python version](tictactoe.py) of the AI, simply run the program in a terminal:

```
> python3 tictactoe.py

-|-|-
-----
-|-|-
-----
-|-|-
Your move: 5

-|-|-
-----
-|X|-
-----
-|-|-
My move: 9

-|-|-
-----
-|X|-
-----
-|-|O
Your move:
```

## Run (C++)
To play against the [C++ version](tictactoe.cpp) of the AI, you can use the provided [Makefile](Makefile):
``` 
> make run
Guaranteed outcome with optimal play (1 = Cross, -1 = nought, 0 = draw): 0
Found in average time out of 100 times: 3.12 ms
Don't trust the AI's determination? Go ahead, try to beat it. You can even go first.

-|-|-
-----
-|-|-
-----
-|-|-
Your move:
```

