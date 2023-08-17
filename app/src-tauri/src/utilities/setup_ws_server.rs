use futures_util::{SinkExt, StreamExt};
use tokio::net::{TcpListener, TcpStream};

use tokio_tungstenite::{accept_async, tungstenite};

use crate::utilities::serial_comm::send_instructions_and_await;

pub async fn start_server() {
    let addr = "127.0.0.1:8080".to_string();

    let try_socket = TcpListener::bind(&addr).await;
    let listener = try_socket.expect("Failed to bind");

    while let Ok((stream, _)) = listener.accept().await {
        println!("Was connected");
        tokio::spawn(accept_connection(stream));
    }
}

pub async fn accept_connection(stream: TcpStream) {
    let ws_stream = accept_async(stream).await.expect("Failed to accept");
    let (mut write, mut read) = ws_stream.split();

    loop {
        tokio::select! {
            // Handle messages from WebSocket
            msg_opt = read.next() => {
                match msg_opt {
                    Some(Ok(msg)) => {
                        let txt_msg = msg.to_text().expect("Error while converting message");
                        let (port, instructions) = txt_msg.split_once(';').unwrap();
                        let microbit_return = send_instructions_and_await(port.to_string(), instructions.to_string()).await;
                        let microbit_msg = tungstenite::Message::text(microbit_return);
                        if let Err(e) = write.send(microbit_msg).await {
                            eprintln!("error while sending to ws: {}", e);
                        }
                    },
                    Some(Err(e)) => {
                        eprintln!("Error while reading from websocket: {}", e);
                    },
                    None => {
                        // WebSocket was closed
                    }
                }
            }
        }
    }
}
