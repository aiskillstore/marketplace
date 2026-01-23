use std::env;
use std::time::{SystemTime, UNIX_EPOCH};

/// Simple random number generator using Linear Congruential Generator
struct Rng {
    state: u64,
}

impl Rng {
    fn new() -> Self {
        // Seed from system time
        let seed = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64;
        Rng { state: seed }
    }

    fn next(&mut self) -> u64 {
        // LCG parameters (same as glibc)
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345);
        self.state
    }

    fn range(&mut self, min: u64, max: u64) -> u64 {
        min + (self.next() % (max - min + 1))
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    // Parse arguments with defaults
    let sides: u64 = args.get(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(6);

    let count: u64 = args.get(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1);

    // Validate inputs
    let sides = sides.clamp(2, 100);
    let count = count.clamp(1, 100);

    // Roll the dice
    let mut rng = Rng::new();
    let mut rolls: Vec<u64> = Vec::new();
    let mut total: u64 = 0;

    for _ in 0..count {
        let roll = rng.range(1, sides);
        rolls.push(roll);
        total += roll;
    }

    // Output as JSON
    let rolls_json: Vec<String> = rolls.iter().map(|r| r.to_string()).collect();
    println!(
        r#"{{"rolls":[{}],"total":{},"sides":{},"count":{}}}"#,
        rolls_json.join(","),
        total,
        sides,
        count
    );
}
