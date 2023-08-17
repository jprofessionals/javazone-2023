from micropython import const

import neopixel
import radio

from microbit import *


class Globals:
    def __init__(self):
        self.MAX_MSG_LENGTH = const(251)

        self.cards = {1057905702: Card(1, True), 1893419794: Card(1, True)}
        self.gameTime = const(20000)  # ms how long one round of the game is
        self.tagDisplayTime = const(
            2000
        )  # ms how long LEDs should show a tag was found

        self.tags = set()
        self.mostRecentTag = 0
        self.isOnTag = False
        self.mostRecentTagTime = 0

        self.fireleds = neopixel.NeoPixel(pin13, 12)

        self.commands = ""
        self.points = 0
        self.runIsStarted = False


class Card:
    def __init__(self, points, isStartPoint):
        self.points = points
        self.isStartPoint = isStartPoint


class RFIDCom:
    READY = 1
    WAITING_FOR_ACK = 2
    WAITING_FOR_RESPONSE = 3


class BusyError(Exception):
    pass


class PN532:
    PN532_ADDRESS = const(0x24)

    PREAMBLE = const(0x00)
    STARTCODE1 = const(0x00)
    STARTCODE2 = const(0xFF)
    POSTAMBLE = const(0x00)

    HOSTTOPN532 = const(0xD4)
    PN532TOHOST = const(0xD5)

    COMMAND_SAMCONFIGURATION = const(0x14)
    COMMAND_RFCONFIGURATION = const(0x32)
    COMMAND_INLISTPASSIVETARGET = const(0x4A)

    ISO14443A = const(0x00)

    ACK = b"\x00\x00\xFF\x00\xFF\x00"
    FRAME_START = b"\x00\x00\xFF"

    I2C_DELAY = 10
    I2C_CARD_POLL_TIMEOUT = 10000

    def __init__(self, i2c):
        self._i2c = i2c
        self.state = RFIDCom.READY
        self.previousCommand = None
        self.previousCommandTime = 0

    def writeData(self, frame):
        # ("write: ", [hex(i) for i in frame])
        self._i2c.write(self.PN532_ADDRESS, frame)

    def writeFrame(self, data):
        length = len(data)
        frame = bytearray(length + 7)
        frame[0] = self.PREAMBLE
        frame[1] = self.STARTCODE1
        frame[2] = self.STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        for x in range(length):
            frame[5 + x] = data[x]
        checksum += sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = self.POSTAMBLE
        self.writeData(bytes(frame))

    def writeCommand(self, command, params=[]):
        data = bytearray(2 + len(params))
        data[0] = self.HOSTTOPN532
        data[1] = command & 0xFF
        for i, val in enumerate(params):
            data[2 + i] = val
        self.writeFrame(data)
        return command

    def readData(self, count):
        frame = self._i2c.read(self.PN532_ADDRESS, count + 1)
        if frame[0] != 0x01:
            raise BusyError
        # print("read: ", [hex(i) for i in frame])
        return frame[1:]

    def readFrame(self, length):
        response = self.readData(length + 8)
        if response[0:3] != self.FRAME_START:
            raise RuntimeError("Invalid response frame start")
        # Check length & length checksum match.
        frameLen = response[3]
        if (frameLen + response[4]) & 0xFF != 0:
            raise RuntimeError("Response length checksum mismatch")
        # Check frame checksum value matches bytes.
        checksum = sum(response[5: 5 + frameLen + 1]) & 0xFF
        if checksum != 0:
            raise RuntimeError("Response checksum mismatch:", checksum)
        # Return frame data.
        return response[5: 5 + frameLen]

    def isReady(self):
        return self._i2c.read(self.PN532_ADDRESS, 1) == b"\x01"

    def gotAck(self):
        return self.readData(len(self.ACK)) == self.ACK

    def getCardId(self, command, responseLen):
        response = self.readFrame(responseLen + 2)
        if not (response[0] == self.PN532TOHOST and response[1] == (command + 1)):
            raise RuntimeError("Invalid card response")
        # Check only 1 card with up to a 7 byte UID is present.
        if response[2] != 0x01 or response[7] > 7:
            raise RuntimeError("Unsupported card response")
        cardId = 0
        for i in range(response[7]):
            cardId = cardId * 256 + response[8 + i]
        return cardId

    def handleRFID(self, globals):
        try:
            currentRFIDTime = running_time()
            if currentRFIDTime < (self.previousCommandTime + self.I2C_DELAY):
                return None

            if (
                    self.previousCommand == self.COMMAND_INLISTPASSIVETARGET
                    and currentRFIDTime
                    > (self.previousCommandTime + self.I2C_CARD_POLL_TIMEOUT)
            ):
                self.state = RFIDCom.READY

            if self.state != RFIDCom.READY and not self.isReady():
                if currentRFIDTime > (self.previousCommandTime + 1000):
                    self.state = RFIDCom.READY
                return None

            self.previousCommandTime = currentRFIDTime

            if self.state == RFIDCom.READY:
                if self.previousCommand is None:
                    self.previousCommand = self.writeCommand(
                        self.COMMAND_SAMCONFIGURATION, params=[0x01, 0x00, 0x01]
                    )
                elif self.previousCommand is self.COMMAND_SAMCONFIGURATION:
                    self.previousCommand = self.writeCommand(
                        self.COMMAND_RFCONFIGURATION, params=[0x01, 0x01]
                    )
                else:
                    self.previousCommand = self.writeCommand(
                        self.COMMAND_INLISTPASSIVETARGET, params=[0x01, self.ISO14443A]
                    )
                self.state = RFIDCom.WAITING_FOR_ACK
            elif self.state == RFIDCom.WAITING_FOR_ACK:
                if self.gotAck():
                    self.state = RFIDCom.WAITING_FOR_RESPONSE
            elif self.state == RFIDCom.WAITING_FOR_RESPONSE:
                if self.previousCommand is self.COMMAND_SAMCONFIGURATION:
                    self.readFrame(0)
                elif self.previousCommand is self.COMMAND_RFCONFIGURATION:
                    self.readFrame(0)
                elif self.previousCommand is self.COMMAND_INLISTPASSIVETARGET:
                    response = self.getCardId(
                        self.COMMAND_INLISTPASSIVETARGET, responseLen=19
                    )

                    if response is None:
                        globals.isOnTag = False
                    else:
                        globals.isOnTag = True

                        if response != globals.mostRecentTag:
                            drive.stop()  # stop the robot and load the next command

                        globals.mostRecentTag = response

                        if response not in globals.tags:
                            globals.tags.add(response)

                            if globals.runIsStarted:
                                globals.mostRecentTagTime = currentRFIDTime
                                print("new card found: ", response)
                                if response in globals.cards:
                                    globals.points = (
                                            globals.points
                                            + globals.cards.get(response).points
                                    )
                                else:
                                    globals.points = response
                                # display.scroll(str(globals.points), wait=False, loop=True)
                        self.state = RFIDCom.READY
                        return response
                self.state = RFIDCom.READY
        except (OSError, RuntimeError, BusyError):
            pass
        return None


class DriveState:
    READY = 1
    TURNING_LEFT = 2
    TURNING_RIGHT = 3
    TURNING_AROUND = 4
    FORWARD = 5


class Drive:
    LF_ADDRESS = const(0x1C)  # address of PCA9557

    LEFT_LF = const(0x01)
    RIGHT_LF = const(0x02)

    TORQUE = 300
    SLOW_TORQUE = 0

    linesPassed = 0
    isOnLine = False

    def __init__(self):
        self.state = DriveState.READY
        self.stop()

    def getLinesensorStatus(self):
        try:
            sleep(10)
            value = i2c.read(self.LF_ADDRESS, 1)

            if value is not None:
                return value[0] & (self.LEFT_LF | self.RIGHT_LF)
        except OSError:
            print("linesensor error")
            pass
        return 0

    def adjustMotors(self, left, right):
        if left >= 0:
            pin16.write_analog(left)
            pin8.write_analog(0)
        else:
            pin16.write_analog(0)
            pin8.write_analog(-left)

        if right >= 0:
            pin14.write_analog(right)
            pin12.write_analog(0)
        else:
            pin14.write_analog(0)
            pin12.write_analog(-right)

    def stop(self):
        self.adjustMotors(0, 0)
        self.state = DriveState.READY

    def turnLeft(self):
        if self.state == DriveState.READY:
            if self.getLinesensorStatus() & self.LEFT_LF:
                self.linesPassed = 0
                self.isOnLine = True
            else:
                self.linesPassed = 1
                self.isOnLine = False
            self.state = DriveState.TURNING_LEFT
            self.adjustMotors(0, self.TORQUE)
        elif self.state == DriveState.TURNING_LEFT:
            self.keepTurning(self.LEFT_LF)

    def keepTurning(self, direction):
        status = self.getLinesensorStatus()
        if self.isOnLine:
            if not (status & direction):
                self.linesPassed += 1
                self.isOnLine = False
        elif status & direction:
            self.isOnLine = True
        if self.linesPassed >= 2:
            self.adjustMotors(self.TORQUE, self.TORQUE)
            self.state = DriveState.FORWARD

    def turnRight(self):
        if self.state == DriveState.READY:
            if self.getLinesensorStatus() & self.RIGHT_LF:
                self.linesPassed = 0
                self.isOnLine = True
            else:
                self.linesPassed = 1
                self.isOnLine = False
            self.state = DriveState.TURNING_RIGHT
            self.adjustMotors(self.TORQUE, 0)
        elif self.state == DriveState.TURNING_RIGHT:
            self.keepTurning(self.RIGHT_LF)

    def turn180(self):
        if self.state == DriveState.READY:
            if self.getLinesensorStatus() & self.LEFT_LF:
                self.linesPassed = 0
                self.isOnLine = True
            else:
                self.linesPassed = 1
                self.isOnLine = False
                self.adjustMotors(-self.TORQUE, self.TORQUE)
            self.state = DriveState.TURNING_AROUND
        elif self.state == DriveState.TURNING_AROUND:
            status = self.getLinesensorStatus()
            if self.isOnLine:
                if not (status & self.LEFT_LF):
                    self.linesPassed += 1
                    self.isOnLine = False
            elif status & self.LEFT_LF:
                self.isOnLine = True

            if self.linesPassed >= 3:
                self.adjustMotors(self.TORQUE, self.TORQUE)
                self.state == DriveState.FORWARD

    def driveForward(self, globals):
        if self.state == DriveState.READY:
            self.state = DriveState.FORWARD

        # for pixel_id in range(0, 11):
        # globals.fireleds[pixel_id] = (0, 0, 0)

        if self.getLinesensorStatus() & self.LEFT_LF:
            self.adjustMotors(self.SLOW_TORQUE, self.TORQUE)
            # for pixel_id in range(0, 5):
            #     globals.fireleds[pixel_id] = (0, 50, 0)
        elif self.getLinesensorStatus() & self.RIGHT_LF:
            self.adjustMotors(self.TORQUE, self.SLOW_TORQUE)
            # for pixel_id in range(6, 11):
            #     globals.fireleds[pixel_id] = (0, 50, 0)
        else:
            self.adjustMotors(self.TORQUE, self.TORQUE)

        # globals.fireleds.show()

    def handleDrive(self, globals):
        if self.state is DriveState.READY:
            if not len(globals.commands):
                return False
            command = globals.commands[0]
            globals.commands = globals.commands[1:]
            if command == "L":
                self.turnLeft()
            elif command == "R":
                self.turnRight()
            elif command == "U":
                self.turn180()
            elif command == "F":
                self.driveForward(globals)
        elif self.state is DriveState.TURNING_LEFT:
            self.turnLeft()
        elif self.state is DriveState.TURNING_RIGHT:
            self.turnRight()
        elif self.state is DriveState.TURNING_AROUND:
            self.turn180()
        elif self.state is DriveState.FORWARD:
            self.driveForward(globals)
        return True


def setLEDs(fireleds, r, g, b, brightness=1.0):
    for pixel_id in range(0, 11):
        fireleds[pixel_id] = (
            int(255.0 * r * brightness),
            int(255.0 * g * brightness),
            int(255.0 * b * brightness),
        )
    fireleds.show()


def initializeNextRun(globals):
    globals.tags.clear()
    globals.mostRecentTag = 0
    globals.isOnTag = False
    globals.mostRecentTagTime = 0
    globals.commands = "FLRLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLULUR"
    while radio.receive_bytes() is not None:
        pass
    globals.runIsStarted = False


def prepareForCommandsDownload(pn532, globals):
    setLEDs(globals.fireleds, 1.0, 1.0, 0, 0.5)
    display.scroll(str(globals.points), wait=False, loop=True)
    pn532.handleRFID(globals)
    if not globals.isOnTag:
        return False

    card = globals.cards.get(globals.mostRecentTag)
    return card and card.isStartPoint


def commandsDownload(globals):
    setLEDs(globals.fireleds, 0, 0, 1.0, 0.5)
    globals.points = 0
    display.scroll(str(globals.points), wait=False, loop=True)
    globals.commands = "LRFU"
    return True


def endRun(globals, drive):
    setLEDs(globals.fireleds, 1.0, 0, 0, 0.5)
    drive.stop()

globals = Globals()

radio.config(length=globals.MAX_MSG_LENGTH, channel=14, power=7, address=0x6795221E)
radio.on()
display.on()
pn532 = PN532(i2c)
drive = Drive()

while True:
    initializeNextRun(globals)

    # while not prepareForCommandsDownload(pn532, globals) or not commandsDownload(globals):
    #     pass

    globals.runIsStarted = True
    currentGameStartTime = running_time()

    # previouslyDisplayedRemainingTime = 6
    # Countdown will start at previouslyDisplayedRemainingTime-1

    while True:
        runningTime = running_time()

        # Exit run if it has used up allowed time
        if runningTime >= (currentGameStartTime + globals.gameTime):
            break

        # Count down seconds remaining
        # remainingTime = int(((currentGameStartTime + gameTime)
        #                 - runningTime) / 1000.0)
        # if remainingTime < previouslyDisplayedRemainingTime:
        #   previouslyDisplayedRemainingTime = remainingTime
        #   display.scroll(remainingTime, wait=False)

        pn532.handleRFID(globals)

        if not drive.handleDrive(globals):
            break

        # Light up LEDs if tag is found
        if globals.mostRecentTagTime != 0 and runningTime <= (
                globals.mostRecentTagTime + globals.tagDisplayTime
        ):
            setLEDs(
                globals.fireleds,
                0,
                1.0,
                0,
                ((globals.mostRecentTagTime + globals.tagDisplayTime) - runningTime)
                / globals.tagDisplayTime,
                )

    endRun(globals, drive)

    sleep(5000)
