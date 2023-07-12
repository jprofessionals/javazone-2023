#![no_main]
#![no_std]
use src_microbit as _;

use core::str;
use microbit::{
    hal::prelude::*,
    hal::twim,
    hal::uarte,
    hal::uarte::{Baudrate, Parity},
    pac::twim0::frequency::FREQUENCY_A,
};

use cortex_m_rt::entry;
use lsm303agr::{AccelOutputDataRate, Lsm303agr};

use core::fmt::Write;
use heapless::Vec;
use nb::block;

mod serial_setup;
use serial_setup::UartePort;

#[entry]
fn main() -> ! {
    defmt::println!("i2c_driver");
    let board = microbit::Board::take().unwrap();

    let mut serial = {
        let serial = uarte::Uarte::new(
            board.UARTE0,
            board.uart.into(),
            Parity::EXCLUDED,
            Baudrate::BAUD115200,
        );
        UartePort::new(serial)
    };

    defmt::println!("hey");
    let i2c = { twim::Twim::new(board.TWIM0, board.i2c_internal.into(), FREQUENCY_A::K100) };

    // Code from documentation
    let mut sensor = Lsm303agr::new_with_i2c(i2c);
    sensor.init().unwrap();
    sensor.set_accel_odr(AccelOutputDataRate::Hz50).unwrap();
    defmt::println!("hey2");
    loop {
        let mut buffer: Vec<u8, 32> = Vec::new();

        loop {
            let byte = block!(serial.read()).unwrap();

            if byte == 13 {
                break;
            }

            if buffer.push(byte).is_err() {
                write!(serial, "error: buffer full\r\n").unwrap();
                break;
            }
        }

        defmt::println!("hey3");

        if str::from_utf8(&buffer).unwrap().trim() == "accelerometer" {
            while !sensor.accel_status().unwrap().xyz_new_data {}

            let data = sensor.accel_data().unwrap();
            write!(
                serial,
                "Accelerometer: x {} y {} z {}\r\n",
                data.x, data.y, data.z
            )
            .unwrap();
        } else if str::from_utf8(&buffer).unwrap().trim() == "magnetometer" {
            while !sensor.mag_status().unwrap().xyz_new_data {}

            let data = sensor.mag_data().unwrap();
            write!(
                serial,
                "Magnetometer: x {} y {} z {}\r\n",
                data.x, data.y, data.z
            )
            .unwrap();
        } else {
            write!(serial, "error: command not detected\r\n").unwrap();
        }
    }
}
