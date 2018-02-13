/*
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
 */

#include <iostream>
#include <chrono>
#include <vector>
#include <limits>
#include <algorithm>
#include <cmath>

using Bitboard = short;
using Move = Bitboard;

/*
 * Winning patterns encoded in bit patterns.
 * E.g. three in a row in the top row is
 *   448 = 0b111000000
 */
constexpr Bitboard WINNING_PATTERS [] =
{
    448,  56,  7,  // Rows
    292, 146, 73,  // Columns
    273, 84        // Diagonals
};

enum Player {
    CROSS = 0, NOUGHT
};

struct SearchResult {
    int score;
    Move move;
};

struct GameResult {
    bool decided;
    int score;
};

/*
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
*/
class Board {
private:
    int _depth;
    Player _turn;
    Bitboard _squares[2];

public:
    Board(Bitboard cross_board = 0,
          Bitboard nought_board = 0,
          Player turn = CROSS,
          int depth = 0)
        : _depth(depth),
        _turn(turn),
        _squares{cross_board, nought_board} {}

    /*
     * Return +1 if _turn has won, -1 for loss and 0 otherwise."
     */
    int score() const {
        for (int player = CROSS; player <= NOUGHT; ++player)
            for (const Bitboard &pattern : WINNING_PATTERS)
                if ((_squares[player] & pattern) == pattern)
                    return player == _turn ? 1 : -1;
        return 0;
    }

    /*
     * Return {b, s} where b is true if the game is over, and s is the score.
     */
    GameResult is_over() const {
        const int s = score();
        return { s != 0 or _depth == 9, s };
    }

    /*
     * Return vector of all possible moves.
     * All unoccupied squares is a move.
     */
    std::vector<Move> moves() const {
        std::vector<Move> m;
        const Bitboard taken = _squares[CROSS] | _squares[NOUGHT];
        Bitboard square = 256;  // Bottom right corner.
        while (square) {
            if (not (taken & square))
                m.push_back(square);
            square = square >> 1;
        }
        return m;
    }

    /*
     * Return a board where the suggested move has been made.
     */
    Board do_move(const Move &move) const {
        Board b(_squares[CROSS],
                _squares[NOUGHT],
                _turn == CROSS ? NOUGHT : CROSS,
                _depth + 1);
        b._squares[_turn] |= move;
        return b;
    }

    /* Allow printing the board to an ostream, e.g. std::cout. */
    friend std::ostream& operator<<(std::ostream&, const Board&);
};

std::ostream& operator<<(std::ostream &strm, const Board &b) {
    for (int i = 0; i < 9; ++i) {
        if ((b._squares[CROSS] & (1 << i))) strm << 'X';
        else if ((b._squares[NOUGHT] & (1 << i))) strm << 'O';
        else strm << '-';
        if (i % 3 < 2) strm << '|';
        else if (i < 8) strm << "\n------\n";
    }
    return strm;
}

/*
 * Return score and best move, relative to board.turn.
 *
 * The search is an implementation of a depth-unlimited
 * Negamax-algorithm, a variant of Minimax.
 */
SearchResult search(const Board &board, int lower = -1, int upper = 1) {

    // If game is over we know the score.
    GameResult game_result = board.is_over();
    if (game_result.decided)
        return {game_result.score, 0};


    // Recursively explore the available moves, keeping
    // track fo the best score and move to play.
    Move best_move;
    int best_score = std::numeric_limits<int>::min();

    for (const Move &move : board.moves()) {

        // v is the score of the position after the move.
        int v = - search(board.do_move(move), -upper, -lower).score;

        // New best move?
        if (v > best_score) {
            best_score = v;
            best_move = move;
        }

        // Update lower bound. Guaranteed at least a score of max(lower, v).
        lower = std::max(lower, v);

        // Pruning: If lower bound equals the upper bound, the true score
        // must be the currently best score. No need to explore other branches.
        if (lower >= upper)
            break;
    }

    return { best_score, best_move };
}

/*
 * Play against the AI in a simple text interface.
 */
void play() {
    Board board;
    char input;
    GameResult game_result;
    while (true) {
        std::cout << '\n' << board << std::endl;

        game_result = board.is_over();
        if (game_result.decided) {
            printf("You lost\nPlay again? (y/n)  ");
            std::cin >> input;
            if (input == 'y' or input == 'Y')
                play();
            break;
        }

        // We query the user until she enters a legal move.
        Move m = -1;
        std::vector<Move> move_list = board.moves();
        while (std::find(move_list.begin(), move_list.end(), m) == move_list.end()) {
            printf("Your move:  ");
            std::cin >> input;
            input -= '0';
            try {
                if (input < 1 or input > 9) throw std::out_of_range("");
                m = 1 << (input - 1);
            } catch(const std::out_of_range &err) {
                if (input + '0' == 'q')
                    return;
                printf("Input a move like 3 for top right (or type q to quit)\n");
            }
        }
        board = board.do_move(m);

        std::cout << '\n' << board << std::endl;

        game_result = board.is_over();
        if (game_result.decided and game_result.score == 0) {
            printf("It's a draw\nPlay again? (y/n)  ");
            std::cin >> input;
            if (input == 'y' or input == 'Y')
                play();
            break;
        }

        SearchResult result = search(board);
        printf("My move = %d\n", (int) (std::round(std::log2(result.move)) + 1));
        board = board.do_move(result.move);

    }
}
int main() {
    auto start_time = std::chrono::high_resolution_clock::now();

    constexpr int N_ITERATIONS = 100;
    Board b;
    SearchResult res;
    for (int iter = 0; iter < N_ITERATIONS; ++iter)
        res = search(b);

    auto total_time = std::chrono::duration_cast<std::chrono::microseconds>
                    (
                     std::chrono::high_resolution_clock::now() - start_time
                     ).count() / (double) N_ITERATIONS;
    printf("Guaranteed outcome with optimal play "
           "(1 = Cross, -1 = nought, 0 = draw): %d\n", res.score);
    printf("Found in average time out of %d times: %.2f ms\n",
            N_ITERATIONS, total_time * (double) 1e-3);
    printf("Don't trust the AI's determination? Go ahead, try to beat it. "
           "You can even go first.\n");

    play();
    return 0;
}
