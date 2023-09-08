from micropython import const

import neopixel
import radio
from microbit import *


class Globals:
    def __init__(self):
        self.CURRENT_ROBOT = 0

        self.robots = [Robot(0.90, 1.0, True),
                       Robot(0.85, 1.0, True),
                       Robot(1.0, 0.83, False),
                       Robot(0.90, 1.0, True)]

        # Day 1 cards
        # self.cards = {
        #     1944688892: Card(3),  # A1
        #     2214546422: Card(0, True),  # A2
        #     3287137276: Card(1),  # A3
        #     871609077: Card(1),  # A4
        #     4081897461: Card(2),  # A5

        #     3004060668: Card(-2),  # B1
        #     1944446709: Card(1),  # B2
        #     1676494582: Card(2),  # B3
        #     329147126: Card(1),  # B4
        #     3543034358: Card(-3),  # B5

        #     2735262972: Card(1),  # C1
        #     2481922550: Card(2),  # C2
        #     3010023420: Card(-1),  # C3
        #     864110588: Card(1),  # C4
        #     601800188: Card(1),  # C5

        #     3813451004: Card(3),  # D1
        #     3019725814: Card(1),  # D2
        #     1667070454: Card(2),  # D3
        #     868100604: Card(-1),  # D4
        #     3278031868: Card(6),  # D5
        # }

        # Day 2 cards
        self.cards = {
            1944688892: Card(2),  # A1
            2214546422: Card(0, True),  # A2
            3287137276: Card(1),  # A3
            871609077: Card(2),  # A4
            4081897461: Card(2),  # A5

            3004060668: Card(1),  # B1
            1944446709: Card(1),  # B2
            1676494582: Card(-2),  # B3
            329147126: Card(1),  # B4
            3543034358: Card(1),  # B5

            2735262972: Card(1),  # C1
            2481922550: Card(-2),  # C2
            3010023420: Card(6),  # C3
            864110588: Card(-1),  # C4
            601800188: Card(-1),  # C5

            3813451004: Card(2),  # D1
            3019725814: Card(1),  # D2
            1667070454: Card(1),  # D3
            868100604: Card(1),  # D4
            3278031868: Card(3),  # D5
        }

        self.MAX_MSG_LENGTH = 251

        self.game_timeout = 4000
        self.tagDisplayTime = 500

        self.tags = set()
        self.mostRecentTag = 0
        self.isOnTag = False
        self.mostRecentScoreEarnedTime = 0
        self.mostRecentTagCrossedTime = 0

        self.fireleds = neopixel.NeoPixel(pin13, 12)

        self.commands = ""
        self.points = 0
        self.runIsStarted = False


class Card:
    def __init__(self, points, isStartCard=False):
        self.points = points
        self.isStartCard = isStartCard

class Robot:
    def __init__(self, leftCalibrate, rightCalibrate, useCollisionDetection):
        self.leftCalibrate = leftCalibrate
        self.rightCalibrate = rightCalibrate
        self.useCollisionDetection = useCollisionDetection


class RFIDCom:
    READY = 1
    WAITING_FOR_ACK = 2
    WAITING_FOR_RESPONSE = 3


class BusyError(Exception):
    pass


class PN532:
    PN532_ADDRESS = 0x24

    PREAMBLE = 0x00
    STARTCODE1 = 0x00
    STARTCODE2 = 0xFF
    POSTAMBLE = 0x00

    HOSTTOPN532 = 0xD4
    PN532TOHOST = 0xD5

    COMMAND_SAMCONFIGURATION = 0x14
    COMMAND_RFCONFIGURATION = 0x32
    COMMAND_INLISTPASSIVETARGET = 0x4A

    ISO14443A = 0x00

    ACK = b"\x00\x00\xFF\x00\xFF\x00"
    FRAME_START = b"\x00\x00\xFF"

    I2C_DELAY = 10
    I2C_CARD_POLL_TIMEOUT = 10000
    I2C_CARD_TAG_TIMEOUT = 100

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

            if self.previousCommand == self.COMMAND_INLISTPASSIVETARGET:
                if (
                    currentRFIDTime >
                    (self.previousCommandTime + self.I2C_CARD_TAG_TIMEOUT)
                ):
                    globals.isOnTag = False

                if (
                    currentRFIDTime >
                    (self.previousCommandTime + self.I2C_CARD_POLL_TIMEOUT)
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

                    if response != 0:
                        globals.isOnTag = True

                        if response != globals.mostRecentTag:
                            # send the tag to the server
                            globals.mostRecentTagCrossedTime = currentRFIDTime
                            print(str(response))
                            radio.send(str(response))
                            drive.stop()  # stop the robot and load the next command

                        globals.mostRecentTag = response

                        if response not in globals.tags:
                            globals.tags.add(response)

                            if globals.runIsStarted:
                                globals.mostRecentScoreEarnedTime = currentRFIDTime
                                # print("new card found: ", response)
                                if response in globals.cards:
                                    globals.points = (
                                            globals.points
                                            + globals.cards.get(response).points
                                    )
                                # else:
                                #     globals.points = response
                                display.scroll(
                                    str(globals.points), wait=False, loop=True
                                )
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

    TORQUE = 400
    TURN_TORQUE = 250
    SLOW_TURN_TORQUE = 0
    SLOW_TORQUE = 0

    EXPECTED_TURN_TIME = 440  # ms
    EXPECTED_U_TURN_TIME = 1000  # ms

    linesPassed = 0
    startedTurning = 0
    isOnLine = False

    def __init__(self, globals):
        self.globals = globals
        self.state = DriveState.READY
        self.stop()

    def getLinesensorStatus(self):
        try:
            value = i2c.read(self.LF_ADDRESS, 1)
            if value is not None:
                return value[0] & (self.LEFT_LF | self.RIGHT_LF)
        except OSError:
            pass
        return 0

    def adjustMotors(self, left, right):
        robot = self.globals.robots[self.globals.CURRENT_ROBOT]

        if left >= 0:
            pin16.write_analog(left*robot.leftCalibrate)
            pin8.write_analog(0)
        else:
            pin16.write_analog(0)
            pin8.write_analog(-left*robot.leftCalibrate)

        if right >= 0:
            pin14.write_analog(right*robot.rightCalibrate)
            pin12.write_analog(0)
        else:
            pin14.write_analog(0)
            pin12.write_analog(-right*robot.rightCalibrate)

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
            self.adjustMotors(-self.SLOW_TURN_TORQUE, self.TURN_TORQUE)
            self.startedTurning = running_time()
        elif self.state == DriveState.TURNING_LEFT:
            self.keepTurning(self.LEFT_LF)

    def keepTurning(self, direction):
        status = self.getLinesensorStatus()
        if (
                (status & direction)
                and (running_time() - self.startedTurning) > self.EXPECTED_TURN_TIME
        ):
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
            self.adjustMotors(self.TURN_TORQUE, -self.SLOW_TURN_TORQUE)
            self.startedTurning = running_time()
        elif self.state == DriveState.TURNING_RIGHT:
            self.keepTurning(self.RIGHT_LF)

    def turn180(self):
        if self.state == DriveState.READY:
            self.startedTurning = running_time()
            if self.getLinesensorStatus() & self.LEFT_LF:
                self.linesPassed = 0
                self.isOnLine = True
            else:
                self.linesPassed = 1
                self.isOnLine = False
            self.adjustMotors(-self.TURN_TORQUE, self.TURN_TORQUE)
            self.state = DriveState.TURNING_AROUND
        elif self.state == DriveState.TURNING_AROUND:
            status = self.getLinesensorStatus()
            if (
                    status & self.LEFT_LF
                    and running_time() - self.startedTurning > self.EXPECTED_U_TURN_TIME
            ):
                self.adjustMotors(self.TORQUE, self.TORQUE)
                self.state = DriveState.FORWARD

    def driveForward(self):
        if self.state == DriveState.READY:
            self.state = DriveState.FORWARD

        if self.getLinesensorStatus() & self.LEFT_LF:
            self.adjustMotors(self.SLOW_TORQUE, self.TORQUE)
        elif self.getLinesensorStatus() & self.RIGHT_LF:
            self.adjustMotors(self.TORQUE, self.SLOW_TORQUE)
        else:
            self.adjustMotors(self.TORQUE, self.TORQUE)

    def handleDrive(self):
        if self.state is DriveState.READY:
            if not len(self.globals.commands):
                return False
            command = self.globals.commands[0]
            self.globals.commands = self.globals.commands[1:]
            if command == "S":
                self.globals.tags.clear()
                self.globals.points = 0
                display.scroll("0", wait=False, loop=True)
            elif command == "L":
                self.turnLeft()
            elif command == "R":
                self.turnRight()
            elif command == "U":
                self.turn180()
            elif command == "F":
                self.driveForward()
        elif self.state is DriveState.TURNING_LEFT:
            self.turnLeft()
        elif self.state is DriveState.TURNING_RIGHT:
            self.turnRight()
        elif self.state is DriveState.TURNING_AROUND:
            self.turn180()
        elif self.state is DriveState.FORWARD:
            self.driveForward()
        return True


def setLEDs(fireleds, r, g, b, brightness=1.0, count=6):
    for pixel_id in range(min(6, count)):
        fireleds[pixel_id] = fireleds[pixel_id + 6] = (
            int(255.0 * r * brightness),
            int(255.0 * g * brightness),
            int(255.0 * b * brightness)
        )

    if count < 6:
        for pixel_id in range(count, 6):
            fireleds[pixel_id] = fireleds[pixel_id + 6] = (0, 0, 0)

    fireleds.show()


def initializeNextRun(globals, drive):
    drive.stop()
    globals.mostRecentTag = 0
    globals.isOnTag = False
    globals.mostRecentScoreEarnedTime = 0
    globals.mostRecentTagCrossedTime = 0
    globals.commands = ""
    while radio.receive_bytes() is not None:
        pass
    globals.runIsStarted = False


def prepareForCommandsDownload(pn532, drive, globals):
    pn532.handleRFID(globals)
    if not globals.isOnTag:
        setLEDs(globals.fireleds, 1.0, 1.0, 0, 0.5)

    return globals.isOnTag


def commandsDownload(globals):
    globals.commands = radio.receive_bytes()

    if (
        not globals.isOnTag
        or globals.commands is None
        or len(globals.commands) == 0
    ):
        if (
                globals.mostRecentTag in globals.cards
                and globals.cards.get(globals.mostRecentTag).isStartCard
        ):
            setLEDs(globals.fireleds, 0, 0, 1.0, 0.5)
        else:
            setLEDs(globals.fireleds, 1.0, 0, 1.0, 0.5)

        return False

    globals.commands = str(globals.commands, "utf8")

    if globals.commands[0] == 'S':
        if globals.mostRecentTag not in globals.cards:
            globals.commands = ""
            return False

        if not globals.cards.get(globals.mostRecentTag).isStartCard:
            globals.commands = ""
            return False

    return True


def endRun(globals, drive):
    drive.stop()

    for i in range(5):
        print(str("RUN_END " + str(globals.points)))
        radio.send(str("RUN_END " + str(globals.points)))


display.on()
globals = Globals()
pn532 = PN532(i2c)
drive = Drive(globals)

radio.config(length=globals.MAX_MSG_LENGTH, channel=14, power=7, address=0x6795221E)
radio.on()


while True:
    initializeNextRun(globals, drive)

    while (
        not prepareForCommandsDownload(pn532, drive, globals)
        or not commandsDownload(globals)
    ):
        pass

    setLEDs(globals.fireleds, 0, 0, 0, 0)
    globals.runIsStarted = True
    globals.mostRecentTagCrossedTime = running_time()
    try:
        while True:
            runningTime = running_time()
            if runningTime >= (globals.mostRecentTagCrossedTime + globals.game_timeout):
                # TODO: only send if car is not on a tag
                print("TIMEOUT")
                radio.send("TIMEOUT")
                break

            if (
                    globals.robots[globals.CURRENT_ROBOT].useCollisionDetection
                    and pin1.read_digital() == 0
            ):
                print("CRASH")
                radio.send("CRASH")
                break

            pn532.handleRFID(globals)

            if not drive.handleDrive():
                break
            if globals.mostRecentScoreEarnedTime != 0 and runningTime <= (
                    globals.mostRecentScoreEarnedTime + globals.tagDisplayTime
            ):
                tagPoints = 0
                if globals.mostRecentTag in globals.cards:
                    tagPoints = globals.cards.get(globals.mostRecentTag).points

                r = 0.0
                g = 1.0
                if tagPoints < 0:
                    r = 1.0
                    g = 0.0

                setLEDs(
                    globals.fireleds,
                    r,
                    g,
                    0,
                    ((globals.mostRecentScoreEarnedTime + globals.tagDisplayTime) - runningTime)
                    / globals.tagDisplayTime,
                    2 + abs(tagPoints)
                )
    except Exception as e:
        exception_text = "Exception: " + str(e) + "\n"

        chunk_size = globals.MAX_MSG_LENGTH
        for i in range(0, len(exception_text), chunk_size):
            chunk = exception_text[i:i+chunk_size]
            print(chunk)
            radio.send(chunk)

        display.show(Image.SKULL)
    endRun(globals, drive)
