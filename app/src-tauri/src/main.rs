use app::utilities::{
    bt_connect::connect,
    bt_scan::{bt_scanner, Device},
    flash_to_microbit::{self, FlashToMicrobit},
};

use tauri::{generate_handler, Builder, Manager};
#[tauri::command]
async fn get_bt() -> Result<Vec<Device>, String> {
    println!("get_bt");
    bt_scanner().await.map_err(|err| err.to_string())
}

#[tauri::command]
async fn connect_to_bt_device(device: String) -> Result<Vec<Device>, String> {
    println!("Connect to bt device");
    connect(device).await.map_err(|err| err.to_string())
}

#[tauri::command]
fn flash_display_nrf(display: FlashToMicrobit) -> String {
    println!("Flashing");
    println!("Flashing: {:?}", display);

    flash_to_microbit::flash_display_nrf(display);

    "Hello You've been greeted from Rust!".to_string()
}

fn main() {
    pretty_env_logger::init();

    Builder::default()
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_window("main").unwrap();
                // window.open_devtools();
            }
            Ok(())
        })
        .invoke_handler(generate_handler![
            flash_display_nrf,
            get_bt,
            connect_to_bt_device
        ])
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
