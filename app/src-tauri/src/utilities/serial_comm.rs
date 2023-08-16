use std::{
    io::{BufRead, BufReader},
    time::Duration,
};

use tokio::time::sleep;

pub const BAUD_RATE: u32 = 115200;

pub async fn send_instructions_and_await(port_name: String, instructions: String) -> String {
    let mut port = serialport::new(port_name, BAUD_RATE)
        .timeout(Duration::from_millis(1000))
        .open()
        .expect("Failed to open port");

    println!(
        "Writing '{}' to {} at {} baud",
        &instructions, &port_name, &BAUD_RATE
    );
    let _ = port.write(instructions.as_bytes());
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

pub async fn send_message(port_name: String, message: String) {
    let mut port = serialport::new(port_name.clone(), BAUD_RATE)
        .timeout(Duration::from_millis(1000))
        .open()
        .expect("Failed to open port");

    let _ = port.write(message.as_bytes());

    sleep(Duration::from_secs(3)).await;
}
