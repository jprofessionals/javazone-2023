use std::time::Duration;

use app::utilities::bt_scan::{bt_scan, bt_scanner, Device};
use tauri::{command, generate_handler, Builder};
use tokio::time::sleep;

#[command]
async fn get_bt_devices_command() -> Result<Vec<Device>, String> {
    bt_scanner().await.map_err(|err| err.to_string())
}

fn main() {
    Builder::default()
        .invoke_handler(generate_handler![get_bt_devices_command])
        .run(tauri::generate_context!())
        .expect("Error while running tauri app");
}

// #[tauri::command]
// fn scan_bt_tt() -> Vec<u8> {
//     println!("Scanning");
//     return bt_scan();
// }
// #[tokio::main]
// async fn main() {
//     tauri::Builder::default()
//         .invoke_handler(tauri::generate_handler![flash_display_nrf])
//         .invoke_handler(tauri::generate_handler![scan_bt_tt])
//         .run(tauri::generate_context!())
//         .expect("error while running tauri application");
// }
