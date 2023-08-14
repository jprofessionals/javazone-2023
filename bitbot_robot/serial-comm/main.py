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
        #sleep(6000)
        for x in data_received:
            if x == 70:
                display.show(Image.ARROW_N)
            elif x == 76:
                display.show(Image.ARROW_W)
            elif x == 82:
                display.show(Image.ARROW_E)
            elif x == 85:
                display.show(Image.ARROW_S)
        sleep(15_000)
        uart.write('{"score":23,"found":[1,2,3,4,5,6,10,11,14,18,19,20,21,1,2,3,4,5,6,10,11,14,18,19,20,21,1,2,3,4,5,6,10,11,14,18,19,20,21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21, 21,1,2,3,4,5,6,10,11,14,18,19,20,21]}\n')