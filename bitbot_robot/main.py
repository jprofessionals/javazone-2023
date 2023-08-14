from microbit import *
from micropython import const
import neopixel
import radio


class Card:
    def __init__(self, points):
        self.points = points


cards = {1057905702: Card(1),
         1893419794: Card(1)}


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

_I2C_DELAY = 10
_I2C_CARD_POLL_TIMEOUT = 10000


class BusyError(Exception):
    pass


class PN532:
    def __init__(self, i2c):
        self._i2c = i2c
        self.state = RFIDCom.READY
        self.previousCommand = None
        self.previousCommandTime = 0
        return

    def _write_data(self, frame):
        # ("write: ", [hex(i) for i in frame])
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
        if frame[0] != 0x01:
            raise BusyError
        # print("read: ", [hex(i) for i in frame])
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
        return self._i2c.read(_I2C_ADDRESS, 1) == b"\x01"

    def got_ack(self):
        return self._read_data(len(_ACK)) == _ACK

    def get_card_id(self, command, response_length):
        response = self._read_frame(response_length + 2)
        if not (response[0] == _PN532TOHOST and response[1] == (command + 1)):
            raise RuntimeError("Invalid card response")
        # Check only 1 card with up to a 7 byte UID is present.
        if response[2] != 0x01 or response[7] > 7:
            raise RuntimeError("Unsupported card response")
        card_id = 0
        for i in range(response[7]):
            card_id = card_id * 256 + response[8 + i]
        return card_id

    def handle_rfid(self):
        try:
            currentRFIDTime = running_time()
            if currentRFIDTime < (self.previousCommandTime + _I2C_DELAY):
                return None

            if (
                self.previousCommand == _COMMAND_INLISTPASSIVETARGET
                and currentRFIDTime
                > (self.previousCommandTime + _I2C_CARD_POLL_TIMEOUT)
            ):
                self.state = RFIDCom.READY

            if self.state != RFIDCom.READY and not self.is_ready():
                if currentRFIDTime > (self.previousCommandTime + 1000):
                    self.state = RFIDCom.READY
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
                self.state = RFIDCom.WAITING_FOR_ACK
            elif self.state == RFIDCom.WAITING_FOR_ACK:
                if self.got_ack():
                    self.state = RFIDCom.WAITING_FOR_RESPONSE
            elif self.state == RFIDCom.WAITING_FOR_RESPONSE:
                if self.previousCommand is _COMMAND_SAMCONFIGURATION:
                    self._read_frame(0)
                elif self.previousCommand is _COMMAND_RFCONFIGURATION:
                    self._read_frame(0)
                elif self.previousCommand is _COMMAND_INLISTPASSIVETARGET:
                    response = self.get_card_id(
                        _COMMAND_INLISTPASSIVETARGET, response_length=19
                    )
                    if response is not None:
                        global tags
                        if response not in tags:
                            tags.add(response)
                            global mostRecentTagTime
                            mostRecentTagTime = currentRFIDTime
                            print("new card found: ", response)
                            global cards
                            global points
                            if response in cards:
                                points = points + cards.get(response).points
                            else:
                                points = response
                            display.scroll(str(points), wait=False, loop=True)
                        self.state = RFIDCom.READY
                        return response
                self.state = RFIDCom.READY
        except (OSError, RuntimeError, BusyError):
            pass
        return None


gameTime = 20000  # ms how long one round of the game is
tagDisplayTime = 2000  # ms how long LEDs should show a tag was found

tags = set()
mostRecentTagTime = 0

fireleds = neopixel.NeoPixel(pin13, 12)

points = 0


def setLEDs(r, g, b, brightness=1.0):
    for pixel_id in range(0, 11):
        fireleds[pixel_id] = (
            int(255.0 * r * brightness),
            int(255.0 * g * brightness),
            int(255.0 * b * brightness),
        )
    fireleds.show()


def initializeNextRun():
    setLEDs(0, 0, 0, 0.0)
    global tags
    tags.clear()
    global mostRecentTagTime
    mostRecentTagTime = 0
    global points
    points = 0
    display.scroll(str(points), wait=False, loop=True)


def endRun():
    setLEDs(1.0, 0, 0, 0.5)
    pass


radio.config(channel=7, power=7)
radio.on()
display.on()

i2c.init()
if _I2C_ADDRESS not in i2c.scan():
    display.scroll("PN532 NOT found!!!", wait=True, loop=True)

pn532 = PN532(i2c)

while True:
    initializeNextRun()
    currentGameStartTime = running_time()

    # previouslyDisplayedRemainingTime = 6
    # Countdown will start at previouslyDisplayedRemainingTime-1

    while True:
        runningTime = running_time()

        # Exit run if it has used up allowed time
        if runningTime >= (currentGameStartTime + gameTime):
            break

        # Count down seconds remaining
        # remainingTime = int(((currentGameStartTime + gameTime)
        #                 - runningTime) / 1000.0)
        # if remainingTime < previouslyDisplayedRemainingTime:
        #   previouslyDisplayedRemainingTime = remainingTime
        #   display.scroll(remainingTime, wait=False)

        pn532.handle_rfid()

        # Light up LEDs if tag is found
        if mostRecentTagTime != 0 and runningTime <= (
            mostRecentTagTime + tagDisplayTime
        ):
            setLEDs(
                0,
                1.0,
                0,
                ((mostRecentTagTime + tagDisplayTime) - runningTime) / tagDisplayTime,
            )

    endRun()

    sleep(5000)
