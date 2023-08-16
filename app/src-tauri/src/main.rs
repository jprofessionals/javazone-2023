use std::sync::Mutex;

use app::utilities::{serial_comm::send_message, setup_ws_server::start_server};

struct DeviceState {
    port: Mutex<String>,
}

use tauri::{generate_handler, Builder};

/// Find all available ports on the computer. Ideally it will find something
/// related to usb.
#[tauri::command]
fn get_available_ports() -> Vec<String> {
    let ports = serialport::available_ports().expect("There to be any ports");
    let ports = ports.iter().map(|ports| ports.port_name.clone()).collect();

    ports
}

// Set and Get function for getting saved usb device
#[tauri::command]
async fn set_device(
    state: tauri::State<'_, DeviceState>,
    device: String,
) -> Result<String, &'static str> {
    send_message(device.clone(), "Ok".to_string()).await;
    *state.port.lock().unwrap() = device;
    Ok("Connected".to_string())
}
#[tauri::command]
fn get_device(state: tauri::State<DeviceState>) -> String {
    println!("Device is now: {}", state.port.lock().unwrap());
    state.port.lock().unwrap().to_string()
}

fn main() {
    pretty_env_logger::init();

    tauri::async_runtime::spawn(start_server());
    Builder::default()
        // .setup(|app| {
        //     #[cfg(debug_assertions)]
        //     {
        //         // Start window with dev tools open in development
        //         let window = app.get_window("main").unwrap();
        //         window.open_devtools();
        //     }
        //     Ok(())
        // })
        .manage(DeviceState {
            port: Default::default(),
        })
        .plugin(tauri_plugin_websocket::init())
        .invoke_handler(generate_handler![
            get_available_ports,
            set_device,
            get_device,
        ])
        .run(tauri::generate_context!())
        .expect("Error while running tauri app");
}
