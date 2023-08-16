use std::sync::Mutex;

use app::utilities::{
    db::{db_get_highscores, db_read_players, db_register_player, SupabaseConfig},
    serial_comm::send_message,
    setup_ws_server::start_server,
};

struct AppState {
    port: Mutex<String>,
    apikey: Mutex<String>,
    url: Mutex<String>,
}

use tauri::{generate_handler, Builder, Manager};

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
    state: tauri::State<'_, AppState>,
    device: String,
) -> Result<String, &'static str> {
    send_message(device.clone(), "Ok".to_string()).await;
    *state.port.lock().unwrap() = device;
    Ok("Connected".to_string())
}

#[tauri::command]
fn get_device(state: tauri::State<AppState>) -> String {
    println!("Device is now: {}", state.port.lock().unwrap());
    state.port.lock().unwrap().to_string()
}

#[tauri::command]
fn set_supabase_config(state: tauri::State<AppState>, url: String, apikey: String) {
    *state.url.lock().unwrap() = url;
    *state.apikey.lock().unwrap() = apikey;
}

#[tauri::command]
fn get_supabase_config(state: tauri::State<AppState>) -> Vec<String> {
    let url = state.url.lock().unwrap().to_string();
    let apikey = state.apikey.lock().unwrap().to_string();
    vec![url, apikey]
}

/// I'm sorry about this confusing function. It turns a struct of AppState that is managed by
/// the tauri app into a simple config struct that can be passed around i.e. not mutex.
fn get_config_from_state(config: tauri::State<'_, AppState>) -> Option<SupabaseConfig> {
    let url = config.url.lock().unwrap().to_string();
    let apikey = config.apikey.lock().unwrap().to_string();

    if url.is_empty() || apikey.is_empty() {
        return None;
    }

    Some(SupabaseConfig { url, apikey })
}

#[tauri::command]
async fn get_players(state: tauri::State<'_, AppState>) -> Result<String, &'static str> {
    let config = get_config_from_state(state);
    if config.is_some() {
        let players = db_read_players(config.unwrap()).await;
        return Ok(players);
    }
    Ok("Please provide config".to_string())
}

#[tauri::command]
async fn get_highscore(state: tauri::State<'_, AppState>) -> Result<String, &'static str> {
    let config = get_config_from_state(state);
    if config.is_some() {
        let config = config.unwrap();
        println!("{}, {}", config.url.clone(), config.apikey.clone());
        let players = db_get_highscores(config).await;
        return Ok(players);
    }
    Ok("Please provide config".to_string())
}

#[tauri::command]
async fn register_player(
    name: String,
    username: String,
    email: Option<String>,
    state: tauri::State<'_, AppState>,
) -> Result<String, &'static str> {
    let config = get_config_from_state(state);
    if config.is_some() {
        let response = db_register_player(name, username, email, config.unwrap()).await;
        return Ok(response);
    }
    Ok("Please provide config".to_string())
}

fn main() {
    pretty_env_logger::init();

    tauri::async_runtime::spawn(start_server());
    Builder::default()
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                // Start window with dev tools open in development
                let window = app.get_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .manage(AppState {
            apikey: Default::default(),
            url: Default::default(),
            port: Default::default(),
        })
        .plugin(tauri_plugin_websocket::init())
        .invoke_handler(generate_handler![
            get_available_ports,
            set_device,
            get_device,
            get_players,
            get_highscore,
            register_player,
            get_supabase_config,
            set_supabase_config
        ])
        .run(tauri::generate_context!())
        .expect("Error while running tauri app");
}
