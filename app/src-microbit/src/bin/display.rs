#![no_main]
#![no_std]

use src_microbit as _;

use microbit::{display::blocking::Display, hal::Timer};

use cortex_m_rt::entry;

#[entry]
fn main() -> ! {
    defmt::println!("Hey there");
    let board = microbit::Board::take().unwrap();

    let mut display = Display::new(board.display_pins);
    let mut timer = Timer::new(board.TIMER0);
    let ledx: [[u8; 5]; 5] = [
        [1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1],
    ];

    let ledy: [[u8; 5]; 5] = [
        [1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ];
    loop {
        display.show(&mut timer, ledx, 30);
    }
}
