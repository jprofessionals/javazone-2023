from microbit import *
import math
import neopixel
import radio

class Command:
    def __init__(self, opcode, duration, useLeftMotor, useRightMotor):
        self.opcode = opcode
        self.duration = duration
        self.useLeftMotor = useLeftMotor
        self.useRightMotor = useRightMotor

speed = 277.0/1000.0  # mm/ms
wheelbase = 117.0  # mm between robot wheels
breakTime = 300  # ms it takes to stop robot

gameTime = 20000  # ms how long one round of the game is
tagDisplayTime = 2000  # ms how long LEDs should show a tag was found

torque = 400.0  # 0-1023 (after adjusting)
leftAdjust = 1.000
rightAdjust = 1.100

commands = []
currentOpcode = ""
currentOpcodeEnd = 0

mostRecentTagTime = 0

fireleds = neopixel.NeoPixel(pin13, 12)

def degreesToLength(degrees):
    return wheelbase*2*(math.pi)*(degrees/360.0)

def lengthToTime(length):
    return length/speed

def drive(useLeftMotor, useRightMotor):
    if useLeftMotor:
        pin16.write_analog(torque*leftAdjust)
        pin8.write_digital(0)

    if useRightMotor:
        pin14.write_analog(torque*rightAdjust)
        pin12.write_digital(0)

def setLEDs(brightness):
    for pixel_id in range(0, 11):
        fireleds[pixel_id] = (0, int(255.0*brightness), 0)
    fireleds.show()

def stop():
    # Left motor
    pin16.write_digital(0)
    pin8.write_digital(0)
    # Left motor
    pin14.write_digital(0)
    pin12.write_digital(0)

def appendForward(length):
    commands.append(Command("forward", lengthToTime(length),
                            True, True))

def appendLeft(degrees):
    commands.append(Command("left", lengthToTime(degreesToLength(degrees)),
                            False, True))

def appendRight(degrees):
    commands.append(Command("right", lengthToTime(degreesToLength(degrees)),
                            True, False))

def initializeNextRun():
    setLEDs(0.0)
    global currentOpcode
    global currentOpcodeEnd
    currentOpcode = ""
    currentOpcodeEnd = 0
    global mostRecentTagTime
    mostRecentTagTime = 0
    commands.clear()
    display.on()
    display.scroll("READY")
    # Example movement. Should be replaced by code uploaded from frontend
    appendForward(200.0)
    appendLeft(90.0)
    appendForward(100.0)
    appendRight(180.0)
    appendForward(100.0)
    appendLeft(90.0)
    appendForward(200.0)

def endRun():
    stop()
    display.off()

radio.config(channel=7, power=7)
radio.on()
while True:
    initializeNextRun()
    currentGameStartTime = running_time()

    previouslyDisplayedRemainingTime = 6
    # Countdown will start at previouslyDisplayedRemainingTime-1

    while True:
        runningTime = running_time()

        # Exit run if it has used up allowed time
        if (runningTime >= (currentGameStartTime + gameTime)):
            break

        # Count down seconds remaining
        remainingTime = int(((currentGameStartTime + gameTime) - runningTime) / 1000.0)
        if remainingTime < previouslyDisplayedRemainingTime:
            previouslyDisplayedRemainingTime = remainingTime
            display.scroll(remainingTime, wait=False)

        # Exit if run is completed
        if not commands and (runningTime >= currentOpcodeEnd):
            break

        # Execute next command if current command is done
        if runningTime >= currentOpcodeEnd:
            if currentOpcode == "":
                command = commands[0]
                currentOpcode = command.opcode
                currentOpcodeEnd = runningTime + command.duration
                drive(command.useLeftMotor, command.useRightMotor)
                commands.pop(0)
            else:
                # Stop robot after each command
                currentOpcodeEnd = currentOpcodeEnd + breakTime
                stop()
                currentOpcode = ""

        # Light up LEDs if tag is found
        if (runningTime <= (mostRecentTagTime + tagDisplayTime)):
            setLEDs(((mostRecentTagTime + tagDisplayTime) - runningTime)
                    / tagDisplayTime)

    endRun()
    break
