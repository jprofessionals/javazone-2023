use std::{
    io::{BufRead, BufReader},
    time::Duration,
};

use tokio::{sync::broadcast, time::sleep};

pub const PORT_NAME: &str = "/dev/tty.usbmodem1402";
pub const BAUD_RATE: u32 = 115200;

pub async fn read_line_from_serial(tx: broadcast::Sender<String>) {
    let mut port = serialport::new(PORT_NAME, BAUD_RATE)
        .timeout(Duration::from_millis(00))
        .open()
        .expect("Failed to open port");

    let mut reader = BufReader::new(&mut port);
    let mut line = String::new();

    loop {
        match reader.read_line(&mut line) {
            Ok(_n) => {
                println!("Read line: {}", line);
                tx.send(line.trim_end_matches('\n').to_string()).unwrap();
                line.clear();
            }
            // Most likely a timeout error, ignore this.
            Err(_e) => {
                continue;
                //eprintln!("Error: {}", e);
            }
        }
    }
}

pub async fn write_to_serial(port: String, message: String) {
    let mut port = serialport::new(port, BAUD_RATE)
        // .data_bits(serialport::DataBits::Eight)
        // .stop_bits(StopBits::Two)
        .timeout(Duration::from_millis(100))
        .open()
        .expect("Failed to open port");

    let _ = port.write(message.as_bytes());

    // How  many seconds to keep connection alive for. TODO: Find out how many seconds we need in
    // order to reliably let bitbot drive around and report back before we "close down" the
    // connection.
    sleep(Duration::from_secs(5)).await;
}
