use app::utilities::{
    bt_scan::{bt_scanner, Device},
    flash_to_microbit::{self, FlashToMicrobit},
};
use tauri::{command, generate_handler, Builder};

#[command]
async fn get_bt_devices_command() -> Result<Vec<Device>, String> {
    bt_scanner().await.map_err(|err| err.to_string())
}

#[tauri::command]
fn flash_display_nrf(display: FlashToMicrobit) -> String {
    println!("Flashing");
    println!("Flashing: {:?}", display);

    flash_to_microbit::flash_display_nrf(display);

    "Hello You've been greeted from Rust!".to_string()
}

fn main() {
    Builder::default()
        .invoke_handler(generate_handler![get_bt_devices_command])
        .invoke_handler(generate_handler![flash_display_nrf])
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
