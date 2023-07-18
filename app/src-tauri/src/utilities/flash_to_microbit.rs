use std::{fs::File, io::Write, process::Command, time::Duration};

use serde::{Deserialize, Serialize};
use wait_timeout::ChildExt;

#[derive(Serialize, Deserialize, Debug)]
pub struct FlashToMicrobit {
    display: Vec<[[u8; 5]; 5]>,
}

pub fn flash_display_nrf(input: FlashToMicrobit) -> String {
    let target_dir = "../src-microbit/attempts/attempt2.json";

    // I have a input that originates as a typescript object with following properties:
    // {
    //   display: number[][][]
    // }
    // And I want to write this as a json file to be read by the microbit
    let commands = serde_json::to_string(&input).unwrap();

    File::create(target_dir)
        .unwrap()
        .write_all(commands.as_bytes())
        .expect("Error writing to file");
    //
    let one_sec = Duration::from_secs(2);
    let mut child = Command::new("sh")
        .current_dir("../src-microbit")
        .arg("-c")
        .arg("cargo rb input_from_build")
        //.arg("probe-run --list-probes")
        .spawn()
        .expect("ls command failed to start");

    let status_code = match child.wait_timeout(one_sec).unwrap() {
        Some(status) => status.code(),
        None => {
            println!("None in status_code");
            child.kill().unwrap();
            child.wait().unwrap().code()
        }
    };

    if status_code.is_some() {
        println!("{:?}", status_code);
    }

    format!("Hello, {}! You've been greeted from Rust!", commands)
}
