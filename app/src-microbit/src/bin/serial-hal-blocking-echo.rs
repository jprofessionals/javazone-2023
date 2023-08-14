#![no_main]
#![no_std]

use defmt::export::display;
use nrf52833_hal::ieee802154;
use src_microbit as _;

use core::fmt::Write;

use microbit::{
    display::blocking::Display,
    hal::prelude::*,
    hal::{ieee802154::Radio, uarte},
    hal::{
        rng::Rng,
        uarte::{Baudrate, Parity},
        Timer,
    },
};

use cortex_m_rt::entry;

mod serial_setup;
use serial_setup::UartePort;

#[entry]
fn main() -> ! {
    let board = microbit::Board::take().unwrap();
    let letter_a = [
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0],
    ];
    let letter_b = [
        [1, 1, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [1, 1, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [1, 1, 0, 0, 0],
    ];
    let mut serial = {
        let serial = uarte::Uarte::new(
            board.UARTE0,
            board.uart.into(),
            Parity::EXCLUDED,
            Baudrate::BAUD115200,
        );
        UartePort::new(serial)
    };
    let mut display = Display::new(board.display_pins);

    let mut timer = Timer::new(board.TIMER0);

    let button_a = board.buttons.button_a.into_floating_input();
    let button_b = board.buttons.button_b.into_floating_input();

    let mut state_a_low = false;
    let mut state_b_low = false;

    let mut rng = Rng::new(board.RNG);

    loop {
        ieee802154::Radio
    }

    // loop {
    //     let button_a_low = button_a.is_low().unwrap();
    //     let button_b_low = button_b.is_low().unwrap();
    //     // Button a pressed down
    //     if button_a_low && !state_a_low {
    //         let rand_num = rng.random_u8();
    //         writeln!(serial, "{}", rand_num).unwrap();
    //         display.show(&mut timer, letter_a, 300)
    //     }
    //     // Button b pressed down
    //     if button_b_low && !state_b_low {
    //         let rand_num = rng.random_u8();
    //         writeln!(serial, "{}", rand_num).unwrap();
    //         display.show(&mut timer, letter_b, 300)
    //     }
    //     // if !button_a_low && state_a_low {
    //     //     write!(serial, "Button A up\n").unwrap();
    //     // }
    //     // if !button_b_low && state_b_low {
    //     //     write!(serial, "Button B up\n").unwrap();
    //     // }
    //     // Store buttons states
    //     // This should not read the GPIO pins again, as the state
    //     // may have changed and the change will not be recorded
    //     state_a_low = button_a_low;
    //     state_b_low = button_b_low;
    //
    //     defmt::println!("Hello there");
    //     let byte = nb::block!(serial.read()).unwrap();
    //     // defmt::println!("Hey");
    //     // if input == b'A' {
    //     //     display.show(&mut timer, letter_a, 300);
    //     // }
    //     // if input == b'B' {
    //     //     display.show(&mut timer, letter_b, 300);
    //     // }
    //     display.show(&mut timer, letter_b, 3000);
    //     //defmt::println!("Done");
    // }

    //
    // loop {
    //     // let mut iv = [0u8; 4];
    //     // rng.fill_bytes(&mut iv);
    //     // defmt::println!("On the road again yo {:?}", iv);
    //     write!(serial, "Hello World {:?} \n", iv).unwrap();
    //     display.show(&mut timer, letter_u, 1000);
    //     // timer.delay_ms(3_000_u32);
    //     // defmt::println!("Waiting");
    // let input = match nb::block!(serial.read()) {
    //     Ok(result) => {
    //         defmt::println!("Read ok!");
    //         result
    //     }
    //     Err(_) => {
    //         defmt::println!("Shit crashed");
    //         0
    //     }
    // };
    // defmt::println!("Hey");
    // write!(serial, "You said: {}\r\n", input as char).unwrap();
    // defmt::println!("Done");
    // }
}
