use std::{
    io::{BufRead, BufReader},
    time::Duration,
};

use app::utilities::{
    bt_connect::connect,
    bt_scan::{bt_scanner, Device},
    flash_to_microbit::{self, FlashToMicrobit},
    serial_comm::{BAUD_RATE, PORT_NAME},
};

use tauri::{generate_handler, Builder};

use futures_util::{SinkExt, StreamExt};
use tokio::{
    net::{TcpListener, TcpStream},
    sync::broadcast,
    time::sleep,
};

use tokio_tungstenite::{accept_async, tungstenite::Result};

async fn start_server() {
    let addr = "127.0.0.1:8080".to_string();

    let try_socket = TcpListener::bind(&addr).await;
    let listener = try_socket.expect("Failed to bind");

    let (tx, mut rx) = broadcast::channel::<String>(10);

    tokio::spawn(async move {
        println!("Starting up async process");
        loop {
            let msg = rx.recv().await;
            println!("From websocket: {:?}", msg);
        }
    });

    // tokio::spawn(read_line_from_serial(tx.clone()));

    while let Ok((stream, _)) = listener.accept().await {
        println!("Was connected");
        tokio::spawn(accept_connection(stream, tx.clone()));
    }
}

async fn accept_connection(stream: TcpStream, tx: broadcast::Sender<String>) {
    let ws_stream = accept_async(stream).await.expect("Failed to accept");
    let (mut write, mut read) = ws_stream.split();
    let mut rx = tx.subscribe();

    loop {
        tokio::select! {
            // Handle messages from WebSocket
            msg_opt = read.next() => {
                match msg_opt {
                    Some(Ok(msg)) => {
                        let txt_msg = msg.to_text().expect("Error while converting message");
                        tx.send(txt_msg.to_string()).expect("Error while sending");
                    },
                    Some(Err(e)) => {
                        eprintln!("Error while reading from websocket: {}", e);
                    },
                    None => {
                        // WebSocket was closed
                        break;
                    }
                }
            }

            // Handle messages from the broadcast channel
            msg_res = rx.recv() => {
                match msg_res {
                    Ok(msg) => {
                        let ws_msg = tokio_tungstenite::tungstenite::Message::text(msg);
                        // Instead of spawning, handle sending within the current context
                        if let Err(e) = write.send(ws_msg).await {
                            eprintln!("error while sending to ws: {}", e);
                        }
                    },
                    Err(_e) => {
                        // All senders are disconnected. Depending on your logic you might want to exit here
                        break;
                    }
                }
            }
        }
    }
}

#[tauri::command]
fn get_available_ports() -> Vec<String> {
    let ports = serialport::available_ports().expect("There to be any ports");
    let ports = ports.iter().map(|ports| ports.port_name.clone()).collect();

    ports
}

#[tauri::command]
async fn connect_to_selected_port(port: String, message: String) {
    println!("uhm");
    let mut port = serialport::new(port, BAUD_RATE)
        // .data_bits(serialport::DataBits::Eight)
        // .stop_bits(StopBits::Two)
        .timeout(Duration::from_millis(100))
        .open()
        .expect("Failed to open port");

    let _ = port.write(message.as_bytes());

    sleep(Duration::from_secs(5)).await;
}

#[tauri::command]
async fn get_bt() -> Result<Vec<Device>, String> {
    println!("get_bt");
    bt_scanner().await.map_err(|err| err.to_string())
}

#[tauri::command]
async fn send_over_serial(message: String) -> String {
    let mut port = serialport::new(PORT_NAME, BAUD_RATE)
        // .data_bits(serialport::DataBits::Eight)
        // .stop_bits(StopBits::Two)
        .timeout(Duration::from_millis(1000))
        .open()
        .expect("Failed to open port");

    let string = "Hey";
    println!(
        "Writing '{}' to {} at {} baud",
        &string, &PORT_NAME, &BAUD_RATE
    );
    //  port.write_data_terminal_ready(true).expect("to be fine");
    let _ = port.write(message.as_bytes());
    sleep(Duration::from_secs(3)).await;
    let mut reader = BufReader::new(&mut port);
    let mut line = String::new();

    loop {
        match reader.read_line(&mut line) {
            Ok(_) => {
                println!("Received data: {}", line.len());
                if !line.trim_end_matches('\n').is_empty() {
                    break;
                }
            }
            Err(e) => {
                println!("received error: {:?}", e);
                continue;
            }
        }
    }

    println!("{}", line);
    line
}

#[tauri::command]
async fn connect_to_bt_device(device: String) -> Result<Vec<Device>, String> {
    println!("Connect to bt device");
    connect(device).await.map_err(|err| err.to_string())
}

// #[tauri::command]
// fn read_from_serial() -> String {
//     serial_comm::read_from_serial();
//     "Ok".to_string()
// }

#[tauri::command]
fn flash_display_nrf(display: FlashToMicrobit) -> String {
    println!("Flashing");
    println!("Flashing: {:?}", display);

    flash_to_microbit::flash_display_nrf(display);

    "Hello You've been greeted from Rust!".to_string()
}

fn main() {
    pretty_env_logger::init();

    tauri::async_runtime::spawn(start_server());
    Builder::default()
        // .setup(|app| {
        //     #[cfg(debug_assertions)]
        //     {
        //         // let window = app.get_window("main").unwrap();
        //         // window.open_devtools();
        //     }
        //     Ok(())
        // })
        .plugin(tauri_plugin_websocket::init())
        .invoke_handler(generate_handler![
            flash_display_nrf,
            get_bt,
            connect_to_bt_device,
            send_over_serial,
            get_available_ports,
            connect_to_selected_port
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
