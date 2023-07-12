// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::fs::File;
use std::io::Write;
use std::process::Command;
use std::time::Duration;
use wait_timeout::ChildExt;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
// #[tauri::command]
// fn greet(name: &str) -> String {
//     format!("Hello, {}! You've been greeted from Rust!", name)
// }

#[tauri::command]
fn flash_display_nrf(commands: &str) -> String {
    println!("{:?}", commands);
    let target_dir = "../src-microbit/attempts/attempt2.json";

    File::create(target_dir)
        .unwrap()
        .write_all(commands.as_bytes())
        .expect("Error writing to file");

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

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![flash_display_nrf])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
