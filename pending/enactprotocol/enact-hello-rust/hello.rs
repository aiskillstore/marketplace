use std::env;

fn main() {
    let name = env::args().nth(1).unwrap_or_else(|| "World".to_string());
    println!("Hello, {}! 🦀", name);
}
