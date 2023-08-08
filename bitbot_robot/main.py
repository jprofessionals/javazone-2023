from microbit import *
from micropython import const
import math
import neopixel
import radio

class RFIDState:
    READY = 1
    PINGED = 2
    PING_COMPLETED = 3
    ACKED = 4
    ACK_COMPLETED = 5

_PREAMBLE = const(0x00)
_STARTCODE1 = const(0x00)
_STARTCODE2 = const(0xFF)
_POSTAMBLE = const(0x00)

_HOSTTOPN532 = const(0xD4)
_PN532TOHOST = const(0xD5)

# PN532 Commands
_COMMAND_SAMCONFIGURATION = const(0x14)
_COMMAND_INLISTPASSIVETARGET = const(0x4A)

_MIFARE_ISO14443A = const(0x00)

# Mifare Commands
MIFARE_CMD_READ = const(0x30)
MIFARE_CMD_WRITE = const(0xA0)
MIFARE_ULTRALIGHT_CMD_WRITE = const(0xA2)

_ACK = b'\x00\x00\xFF\x00\xFF\x00'
_FRAME_START = b'\x00\x00\xFF'

_I2C_ADDRESS = const(0x24)
_NOT_BUSY = const(0x01)


class BusyError(Exception):
    pass

class PN532:
    def __init__(self, i2c, *, irq=None, req=None, debug=False):
        self.debug = debug
        self._irq = irq
        self._req = req
        self._i2c = i2c
        self.state = RFIDState.READY
        self.initialised = False
        return

    def _read_data(self, count):
        if self.debug:
            print("_rd")

        status_byte = self._i2c.read(_I2C_ADDRESS, 1)
        if self.debug:
            print("_rd status_byte: ", status_byte)
        if status_byte[0] != _NOT_BUSY:             # not ready
            if self.debug:
                print("_rd busy_error ")
            raise BusyError
        if self.debug:
            print("_rd readfrom_into")
        frame = self._i2c.read(_I2C_ADDRESS, count)
        if self.debug:
            print("_rd frame: ", frame)
        return frame

    def _write_data(self, framebytes):
        try:
            if self.debug:
                print('_wd: ', [hex(i) for i in framebytes])
            self._i2c.write(_I2C_ADDRESS, framebytes)
        except (OSError, RuntimeError):
            if self.debug:
                print("is_ready exception")

    def _write_frame(self, data):
        """Write a frame to the PN532 with the specified data bytearray."""
        assert data is not None and 1 < len(
            data) < 255, 'Data must be 1-255 bytes.'
        # Build frame to send as:
        # - Preamble (0x00)
        # - Start code  (0x00, 0xFF)
        # - Command length (1 byte)
        # - Command length checksum
        # - Command bytes
        # - Checksum
        # - Postamble (0x00)
        length = len(data)
        frame = bytearray(length+8)
        frame[0] = _PREAMBLE
        frame[1] = _STARTCODE1
        frame[2] = _STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        for x in range(length):
            frame[5+x] = data[x]
        print('Frame:', [hex(i) for i in frame])
        checksum += sum(data)
        frame[-2] = (~checksum & 0xFF)+1
        frame[-1] = _POSTAMBLE
        # Send frame.
        if self.debug:
            print('Write frame: ', [hex(i) for i in frame])
        self._write_data(bytes(frame))

    def write_command(self, command, params=[]):
        data = bytearray(2+len(params))
        data[0] = _HOSTTOPN532
        data[1] = command & 0xFF
        for i, val in enumerate(params):
            data[2+i] = val

        try:
            self._write_frame(data)
        except OSError:
            if self.debug:
                print("write_command OSError")

    def _read_frame(self, length):
        response = self._read_data(length+8)
        if self.debug:
            print('Read frame:', [hex(i) for i in response])

        # Swallow all the 0x00 values that preceed 0xFF.
        offset = 0
        while response[offset] == 0x00:
            offset += 1
            if offset >= len(response):
                raise RuntimeError(
                    'Response frame preamble does not contain 0xFF!')
        if response[offset] != 0xFF:
            raise RuntimeError(
                'Response frame preamble does not contain 0xFF!')
        offset += 1
        if offset >= len(response):
            raise RuntimeError('Response contains no data!')
        # Check length & length checksum match.
        frame_len = response[offset]
        if (frame_len + response[offset+1]) & 0xFF != 0:
            raise RuntimeError(
                'Response length checksum mismatch')
        # Check frame checksum value matches bytes.
        checksum = sum(response[offset+2:offset+2+frame_len+1]) & 0xFF
        if checksum != 0:
            raise RuntimeError(
                'Response checksum mismatch:', checksum)
        # Return frame data.
        return response[offset+2:offset+2+frame_len]

    def is_ready(self):
        status = bytearray(1)
        try:
            status = self._i2c.read(_I2C_ADDRESS, 1)
        except OSError:
            if self.debug:
                print("is_ready exception")
        if status != b'\x00':
            print("status:", status)
        return status == b'\x01'

    def got_ack(self):
        return self._read_data(len(_ACK)) == _ACK

    def get_card_id(self, command, response_length=0):
        response = self._read_frame(response_length+2)
        if not (response[0] == _PN532TOHOST and response[1] == (command+1)):
            raise RuntimeError('Received unexpected command response!')
        return response[2:]

    def handle_rfid(self):
        # return a bytearray with the UID if a card is detected.
        if self.state == RFIDState.READY:
            if not self.initialised:
                # - 0x01, normal mode
                # - 0x02, timeout 50ms * 2 = 100ms
                # - 0x01, use IRQ pin
                self.write_command(_COMMAND_SAMCONFIGURATION,
                                   params=[0x01, 0x02, 0x01])
            else:
                print("ping card")
                self.write_command(_COMMAND_INLISTPASSIVETARGET,
                                   params=[0x01, _MIFARE_ISO14443A])
            self.state = RFIDState.PINGED
        elif self.state == RFIDState.PINGED:
            if self.is_ready():
                self.state = RFIDState.PING_COMPLETED
        elif self.state == RFIDState.PING_COMPLETED:
            print("ping completed")
            if self.got_ack() is True:
                self.state = RFIDState.ACKED
        elif self.state == RFIDState.ACKED:
            print("acked")
            if self.is_ready():
                self.state = RFIDState.ACK_COMPLETED
        elif self.state == RFIDState.ACK_COMPLETED:
            if not self.initialised:
                print("init completed")
                self.initialised = True
                self.state = RFIDState.READY
            else:
                response = self.get_card_id(_COMMAND_INLISTPASSIVETARGET,
                                            response_length=19)
                if response is None:
                    return None

                # Check only 1 card with up to a 7 byte UID is present.
                if response[0] != 0x01:
                    raise RuntimeError('>1 card detected!')
                if response[5] > 7:
                    raise RuntimeError('Found card with long UID!')

                print("card found")
                self.state = RFIDState.READY
                # Return UID of card.
                return response[6:6+response[5]]

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
    if False:  # useLeftMotor:
        pin16.write_analog(torque*leftAdjust)
        pin8.write_digital(0)

    if False:  # useRightMotor:
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

pn532 = PN532(i2c, debug=True)

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

        pn532.handle_rfid()
        # Light up LEDs if tag is found
        if (runningTime <= (mostRecentTagTime + tagDisplayTime)):
            setLEDs(((mostRecentTagTime + tagDisplayTime) - runningTime)
                    / tagDisplayTime)

    endRun()
    break
