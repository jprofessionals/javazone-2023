use std::env;
use std::fs::{self, File};
use std::io::Write;
use std::path::PathBuf;

// macro_rules! p {
//     ($($tokens: tt)*) => {
//         println!("cargo:warning={}", format!($($tokens)*))
//     }
// }

fn main() {
    let file_path = "attempts/attempt2.json";

    let content = fs::read_to_string(file_path).expect("Could not read file");

    // Generate path to output file
    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap()).join("config_data.rs");

    // Write config_data into the output file
    File::create(out_path)
        .unwrap()
        .write_all(content.as_bytes())
        .unwrap();
}
