use std::fmt::Display;
use std::hint::black_box;

const WINNING_PATTERNS: [[usize; 3]; 8] = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
];

#[derive(Copy, Clone)]
enum Player {
    X,
    O,
}

struct State {
    board: [Option<Player>; 9],
    turn: Player,
}

impl State {
    const fn new() -> Self {
        Self {
            board: [None; 9],
            turn: Player::X,
        }
    }

    fn best_move(&mut self) -> usize {
        let (_, best_move) = self.search(-2, 2);
        best_move
    }

    fn search(&mut self, mut lower: i8, upper: i8) -> (i8, usize) {
        if let Some(score) = self.score() {
            return (-score, 0);
        }
        let mut best_move = 0;
        let mut best_score = -2;
        for pos in 0..9 {
            if self.board[pos].is_none() {
                self.do_move(pos);
                let (score, _) = self.search(-upper, -lower);
                self.undo_move(pos);
                if score > best_score {
                    best_score = score;
                    best_move = pos;
                    if score > lower {
                        lower = score;
                        if score >= upper {
                            break;
                        }
                    }
                }
            }
        }
        return (-best_score, best_move);
    }

    fn do_move(&mut self, pos: usize) {
        self.board[pos] = Some(self.turn);
        self.turn = match self.turn {
            Player::X => Player::O,
            Player::O => Player::X,
        }
    }

    fn undo_move(&mut self, pos: usize) {
        self.board[pos] = None;
        self.turn = match self.turn {
            Player::X => Player::O,
            Player::O => Player::X,
        }
    }

    fn score(&self) -> Option<i8> {
        self.absolute_score().map(|score| {
            if let Player::X = self.turn {
                score
            } else {
                -score
            }
        })
    }

    fn absolute_score(&self) -> Option<i8> {
        for pattern in WINNING_PATTERNS.iter() {
            match (
                self.board[pattern[0]],
                self.board[pattern[1]],
                self.board[pattern[2]],
            ) {
                (Some(Player::X), Some(Player::X), Some(Player::X)) => return Some(1),
                (Some(Player::O), Some(Player::O), Some(Player::O)) => return Some(-1),
                _ => (),
            }
        }
        if self.board.iter().all(|p| p.is_some()) {
            return Some(0);
        }
        None
    }
}

impl Display for State {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        writeln!(f, "---+---+---")?;
        for row in self.board.chunks(3) {
            writeln!(
                f,
                "{}",
                row.iter()
                    .map(|p| match p {
                        Some(Player::X) => " X ",
                        Some(Player::O) => " O ",
                        None => "   ",
                    })
                    .collect::<Vec<_>>()
                    .join("|")
            )?;
            writeln!(f, "---+---+---")?;
        }
        Ok(())
    }
}

fn benchmark() {
    let mut state = State::new();
    let samples = 100;
    let now = std::time::Instant::now();
    for _ in 0..samples {
        state = black_box(state);
        state.best_move();
    }
    println!(
        "Best move found in an average of {}ms",
        (now.elapsed().as_millis() as f64) / (samples as f64)
    );
}

fn main() {
    benchmark();

    let mut state = State::new();
    println!("\n{}", state);
    while state.score().is_none() {
        println!("Enter move [0, 9): ");
        let mut input = String::new();
        if std::io::stdin().read_line(&mut input).is_err() {
            continue;
        }
        let input = input.trim().parse::<usize>();
        if input.is_err() {
            continue;
        }
        let pos = input.unwrap();
        if pos >= 9 || state.board[pos].is_some() {
            continue;
        }

        state.do_move(pos);
        println!("{}", state);

        if state.score().is_some() {
            // This will never be true, because of perfect play.
            break;
        }

        let best_move = state.best_move();
        state.do_move(best_move);
        println!("{}", state);
    }

    match state.score() {
        Some(1) => println!("You win!"),
        Some(-1) => println!("You lose!"),
        Some(0) => println!("Draw!"),
        _ => (),
    }
}
