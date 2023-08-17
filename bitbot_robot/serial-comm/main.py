from microbit import *

# Set up the serial connection
uart.init(baudrate=115200)

display.show(Image.BUTTERFLY)

while True:
    display.show(Image.DUCK)

    if button_a.is_pressed():
        display.show(Image.ANGRY)

    if uart.any():
        data_received = uart.read()
        display.scroll(data_received)
        display.show(Image.HEART)
        for x in data_received:
            if x == 70:
                display.show(Image.ARROW_N)
            elif x == 76:
                display.show(Image.ARROW_W)
            elif x == 83:
                display.show(Image.SMILE)
            elif x == 82:
                display.show(Image.ARROW_E)
            elif x == 85:
                display.show(Image.ARROW_S)
            sleep(1_000)
        # Simulate the time i takes for a car to drive around and then report back.
        sleep(5_000)
        uart.write('{"score":7,"found":[1, 2, 4, 6, 7, 8, 9]}\n')