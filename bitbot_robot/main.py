from microbit import *
from micropython import const
import math
import neopixel
import radio


class RFIDCom:
    READY = 1
    WAITING_FOR_ACK = 2
    WAITING_FOR_RESPONSE = 3


_PREAMBLE = const(0x00)
_STARTCODE1 = const(0x00)
_STARTCODE2 = const(0xFF)
_POSTAMBLE = const(0x00)

_HOSTTOPN532 = const(0xD4)
_PN532TOHOST = const(0xD5)

_COMMAND_SAMCONFIGURATION = const(0x14)
_COMMAND_RFCONFIGURATION = const(0x32)
_COMMAND_INLISTPASSIVETARGET = const(0x4A)

_MIFARE_ISO14443A = const(0x00)

_ACK = b"\x00\x00\xFF\x00\xFF\x00"
_FRAME_START = b"\x00\x00\xFF"

_I2C_ADDRESS = const(0x24)
_I2C_READY = const(0x01)

_I2C_DELAY = 10


class BusyError(Exception):
    pass


class PN532:
    def __init__(self, i2c, *, irq=None, req=None, debug=False):
        self.debug = debug
        self._irq = irq
        self._req = req
        self._i2c = i2c
        self.state = RFIDCom.READY
        self.initialised = False
        self.configured = False
        self.previousCommand = None
        self.previousCommandTime = 0
        return

    def _write_data(self, frame):
        print("write: ", [hex(i) for i in frame])
        self._i2c.write(_I2C_ADDRESS, frame)

    def _write_frame(self, data):
        length = len(data)
        frame = bytearray(length + 7)
        frame[0] = _PREAMBLE
        frame[1] = _STARTCODE1
        frame[2] = _STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        for x in range(length):
            frame[5 + x] = data[x]
        checksum += sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = _POSTAMBLE
        self._write_data(bytes(frame))

    def write_command(self, command, params=[]):
        data = bytearray(2 + len(params))
        data[0] = _HOSTTOPN532
        data[1] = command & 0xFF
        for i, val in enumerate(params):
            data[2 + i] = val
        self._write_frame(data)
        return command

    def _read_data(self, count):
        frame = self._i2c.read(_I2C_ADDRESS, count + 1)
        if frame[0] != _I2C_READY:
            raise BusyError
        print("read: ", [hex(i) for i in frame])
        return frame[1:]

    def _read_frame(self, length):
        response = self._read_data(length + 8)
        if response[0:3] != _FRAME_START:
            raise RuntimeError("Invalid response frame start")
        # Check length & length checksum match.
        frame_len = response[3]
        if (frame_len + response[4]) & 0xFF != 0:
            raise RuntimeError("Response length checksum mismatch")
        # Check frame checksum value matches bytes.
        checksum = sum(response[5 : 5 + frame_len + 1]) & 0xFF
        if checksum != 0:
            raise RuntimeError("Response checksum mismatch:", checksum)
        # Return frame data.
        return response[5 : 5 + frame_len]

    def is_ready(self):
        status = bytearray(1)
        try:
            status = self._i2c.read(_I2C_ADDRESS, 1)
        except OSError:
            return False
        return status == b"\x01"

    def got_ack(self):
        return self._read_data(len(_ACK)) == _ACK

    def get_card_id(self, command, response_length):
        print("get_card_id")
        response = self._read_frame(response_length + 2)
        print("get_card_id: ", [hex(i) for i in response])
        if not (response[0] == _PN532TOHOST and response[1] == (command + 1)):
            print("Invalid card response")
            raise RuntimeError("Invalid card response")
        # Check only 1 card with up to a 7 byte UID is present.
        if response[2] != 0x01 or response[7] > 7:
            print("Unsupported card response")
            raise RuntimeError("Unsupported card response")
        return response[8 : 8 + response[7]]

    def handle_rfid(self):
        try:
            currentRFIDTime = running_time()
            if (self.previousCommandTime + _I2C_DELAY) > currentRFIDTime:
                return None

            if self.state != RFIDCom.READY and not self.is_ready():
                return None

            self.previousCommandTime = currentRFIDTime

            if self.state == RFIDCom.READY:
                if self.previousCommand is None:
                    self.previousCommand = self.write_command(
                        _COMMAND_SAMCONFIGURATION, params=[0x01, 0x00, 0x01]
                    )
                elif self.previousCommand is _COMMAND_SAMCONFIGURATION:
                    self.previousCommand = self.write_command(
                        _COMMAND_RFCONFIGURATION, params=[0x01, 0x01]
                    )
                else:
                    self.previousCommand = self.write_command(
                        _COMMAND_INLISTPASSIVETARGET, params=[0x01, _MIFARE_ISO14443A]
                    )
                    # self.write_command(0x60,
                    #                    params=[0x01, 0x01, _MIFARE_ISO14443A])
                self.state = RFIDCom.WAITING_FOR_ACK
            elif self.state == RFIDCom.WAITING_FOR_ACK:
                if self.got_ack():
                    self.state = RFIDCom.WAITING_FOR_RESPONSE
            elif self.state == RFIDCom.WAITING_FOR_RESPONSE:
                if self.previousCommand is _COMMAND_SAMCONFIGURATION:
                    self._read_frame(0)
                    print('SAMConfiguration complete')
                elif self.previousCommand is _COMMAND_RFCONFIGURATION:
                    self._read_frame(0)
                    print('RFConfiguration complete')
                elif self.previousCommand is _COMMAND_INLISTPASSIVETARGET:
                    print("got card?")
                    response = self.get_card_id(
                        _COMMAND_INLISTPASSIVETARGET, response_length=19
                    )
                    if response is not None:
                        print("read: ", [hex(i) for i in response])
                        print("card found: ", response)
                        self.state = RFIDCom.READY
                        return response
                self.state = RFIDCom.READY
        except (OSError, RuntimeError, BusyError):
            pass
        return None


class Command:
    def __init__(self, opcode, duration, useLeftMotor, useRightMotor):
        self.opcode = opcode
        self.duration = duration
        self.useLeftMotor = useLeftMotor
        self.useRightMotor = useRightMotor


speed = 277.0 / 1000.0  # mm/ms
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
    return wheelbase * 2 * (math.pi) * (degrees / 360.0)


def lengthToTime(length):
    return length / speed


def drive(useLeftMotor, useRightMotor):
    if False:  # useLeftMotor:
        pin16.write_analog(torque * leftAdjust)
        pin8.write_digital(0)

    if False:  # useRightMotor:
        pin14.write_analog(torque * rightAdjust)
        pin12.write_digital(0)


def setLEDs(brightness):
    for pixel_id in range(0, 11):
        fireleds[pixel_id] = (0, int(255.0 * brightness), 0)
    fireleds.show()


def stop():
    # Left motor
    pin16.write_digital(0)
    pin8.write_digital(0)
    # Left motor
    pin14.write_digital(0)
    pin12.write_digital(0)


def appendForward(length):
    commands.append(Command("forward", lengthToTime(length), True, True))


def appendLeft(degrees):
    commands.append(
        Command("left", lengthToTime(degreesToLength(degrees)), False, True)
    )


def appendRight(degrees):
    commands.append(
        Command("right", lengthToTime(degreesToLength(degrees)), True, False)
    )


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

i2c.init()
if _I2C_ADDRESS in i2c.scan():
    print("Found PN532")
else:
    print("PN532 NOT found!!!")

pn532 = PN532(i2c, debug=True)
while True:
    pn532.handle_rfid()

while True:
    initializeNextRun()
    currentGameStartTime = running_time()

    previouslyDisplayedRemainingTime = 6
    # Countdown will start at previouslyDisplayedRemainingTime-1

    while True:
        runningTime = running_time()

        # Exit run if it has used up allowed time
        if runningTime >= (currentGameStartTime + gameTime):
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

        pn532.handle_rfid()
        # Light up LEDs if tag is found
        if runningTime <= (mostRecentTagTime + tagDisplayTime):
            setLEDs(
                ((mostRecentTagTime + tagDisplayTime) - runningTime) / tagDisplayTime
            )

    endRun()
    break
