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

import java.util.List;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.InputMismatchException;

class Board {
    private static final int CROSS  = 1;
    private static final int NOUGHT = 2;
    private static final int[][] WINNING_PATTERNS = {{0, 1, 2}, {3, 4, 5}, {6, 7, 8},
                                                     {0, 3, 6}, {1, 4, 7}, {2, 5, 8},
                                                     {0, 4, 8}, {2, 4, 6}};
    private static final int NO_MOVE = -1;
    private int[] squares = new int[9];
    private int turn = CROSS;
    private int depth = 0;

    /**
     * Return the score of the position, in the perspective of turn.
     * @return 1 if turn has a winning position, -1 if losing, 0 otherwise.
     */
    public int score() {
        for (int[] pattern : WINNING_PATTERNS)
            // We have a win if all squares in the pattern are filled with
            // the same non-zero player number.
            if (squares[pattern[0]] != 0
                    && squares[pattern[0]] == squares[pattern[1]]
                    && squares[pattern[1]] == squares[pattern[2]])
                return squares[pattern[0]] == turn ? 1 : -1;
        return 0;
    }

    /**
     * @return True if the game is over, false otherwise.
     */
    public boolean isDecided() {
        return depth == 9 || score() != 0;
    }

    /**
     * Apply the given move to the position.
     * @param move The move to make, a number in [0, 9).
     */
    public void doMove(int move) {
        squares[move] = turn;
        depth++;
        turn = turn == CROSS ? NOUGHT : CROSS;
    }

    /**
     * Undo the given move.
     * @param move The move to undo, a number in [0, 9).
     */
    public void undoMove(int move) {
        squares[move] = 0;
        depth--;
        turn = turn == CROSS ? NOUGHT : CROSS;
    }

    /**
     * @return A list of possible moves from the position.
     */
    public List<Integer> getMoves() {
        List<Integer> moves = new ArrayList<>();
        for (int i = 0; i < 9; i++) {
            if (squares[i] == 0) {
                moves.add(i);
            }
        }
        return moves;
    }

    @Override
    public String toString() {
        char[] symbols = {'-', 'X', 'O'};
        String out = "";
        for (int i = 0; i < 9; i++) {
            out += symbols[squares[i]];
            if (i % 3 < 2) out += "|";
            if (i % 3 == 2 && i < 8) out += "\n";
        }
        return out;
    }

    /**
     * Plain structure class used in search associate values to moves.
     */
    private class SearchResult {
        int value;
        int move;

        SearchResult(int value, int move) {
            this.value = value;
            this.move = move;
        }
    }

    /**
     * @return The optimal move from the position, a number in [0, 9).
     */
    public int bestMove() {
        return search(-1, 1).move;
    }

    /**
     * Depth-unlimited alpha-beta-pruned negamax implementation.
     * @param lower lower bound for score, minimum guaranteed score.
     * @param upper upper bound for score, maximum guaranteed score.
     * @return A SearchResult instance with the best possible move
     *         from the current position, and the corresponding
     *         score obtained from perfect play.
     */
    private SearchResult search(int lower, int upper) {

        // If game is decided, we know the score.
        if (isDecided()) {
            return new SearchResult(score(), NO_MOVE);
        }


        // Search all available moves, keeping the best scoring one.
        SearchResult best = new SearchResult(lower, NO_MOVE);

        for (int move : getMoves()) {
            doMove(move);
            int v = - search(-upper, -lower).value;  // Negamax recursion call.
            undoMove(move);

            // If move is a new best, keep that instead.
            if (v > best.value)
                best = new SearchResult(v, move);

            // Update the lower bound if changed.
            lower = Math.max(lower, v);

            // If the bounded score region is of zero size, nothing we find will
            // change the outcome of the search. The remaining tree can be pruned.
            if (lower >= upper)
                break;
        }
        return best;
    }
}


/**
 * Main class to play against the AI in a command line interface.
 */
class Play {
    public static void main(String[] args) {
        Board board = new Board();
        int bestMove;
        long start = System.nanoTime();
        for (int i = 0; i < 100; i++)
            bestMove = board.bestMove();
        System.out.printf("Found best move in %.2f ms on average of 100 times.\n", (System.nanoTime() - start) / (double) 100000000);
        play();
    }

    static boolean checkDecided(Board board) {
        if (board.isDecided()) {
            Scanner scan = new Scanner(System.in);
            String[] results = {"You lost", "It's a draw", "You won"};
            System.out.println( results[ board.score() + 1 ] );
            System.out.print("Play again? (y/n)  ");
            if (scan.next().toLowerCase().startsWith("y"))
                play();
            return true;
        }
        return false;
    }

    static void play() {
        Board board = new Board();
        Scanner scan = new Scanner(System.in);
        while (true) {
            System.out.println("\n" + board + "\n");

            if (checkDecided(board))
                break;

            int move = -1;
            while (!board.getMoves().contains(move)) {
                System.out.print("Your move: ");
                try {
                    move = scan.nextInt() - 1;
                } catch (InputMismatchException exception) {
                    System.out.println("Enter a number in [1, 9]");
                    scan = new Scanner(System.in);
                }
            }
            board.doMove(move);

            System.out.println("\n" + board);

            if (checkDecided(board))
                break;

            int best = board.bestMove();
            System.out.println("\nMy move: " + (best - 1));
            board.doMove(best);
        }
    }
}

