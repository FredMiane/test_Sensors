# the project SENSORS simulate create an dsimulate a list of sensors:
#  - long range: Lidar (ie 40m)
#  - short range: sonar (ie 20m)
#  - switch input: emergency stop, shock dectection, which stop the movement
#
# When the distance measured by the lidar reach the minRange, we switch to sonar, the we
# go back to Lidar when maxRange of the sonar is reached again
# (for simulation, when we swith from lidar to sonar, we send the lidar last measurment to the
# initilal range value of the sonars)
# The Sensors start from unknown syte, got initialized, then the switches and Lidar are started,
# the sonars are put in sleep mode (low power)
#
# Then according to the distance to an obstacles, we switch from lidar to sonars to lidar,
# as we put them to Run state or Stop state
#
# Switches have a high priority
#
# the main loop state machine start with creating and initialiszinf the sensors according
# to the parameters of the json file  the according to the distance measured we Speed up or Slow down
# Speed is set to zero if deistance is under 1m
#
#
# Tested with Python 3.4.3 and matplotlib 2.2.2

import numpy as np
import matplotlib.pyplot as plt

import json
import os

import time
import copy
import random
import struct
import binascii
from enum import Enum


class State(Enum):
    unknown = 0  # unknow state at start
    initialized = 1  # sensor initialized
    running = 2  # running measurement
    sleeping = 3  # in low power mode if needed
    stopped = 4  # stopped


class StateMachine(Enum):
    init = 0  # init sate
    checkSensors = 1  # check different sensors
    speedUp = 2  # speed up if green light
    slowDown = 3  # slow down if obstacle detected
    Stop = 4  # emergency stop if switch on


stateArray = ["Unknown", "Initialized", "Running", "Sleeping", "Stopped"]
stateArray = ["Unknown", "Initialized", "Running", "Sleeping", "Stopped"]
smArray = ["init", "checksensors", "speedUp", "slowDown", "stop"]

sensorsList = []

speed = 0
max_speed = 40
currentState = StateMachine.init


class Sensor():
    def __init__(self, type, index, minRange, maxRange):
        self.type = type
        self.index = index
        self.state = State.unknown
        self.range = 0
        self.minRange = minRange
        self.maxRange = maxRange

    def initialize(self):
        self.state = State.initialized

    def run(self):
        self.state = State.running

    def sleep(self):
        self.state = State.sleeping

    def stop(self):
        self.state = State.stopped

    def makeMeasurment(self):
        self.range = 0


class Lidar(Sensor):
    def __init__(self, index, minRange, maxRange):
        Sensor.__init__(self, 'lidar', index, minRange, maxRange)
        self.index = index
        print("new Lidar" + repr(self.index))

    def initialize(self):
        Sensor.initialize(self)
        # do something specific to Lidar
        self.range = (self.minRange + self.maxRange)/2  # initialize to half range

    def makeMeasurment(self):
        self.range = self.range + random.randint(-2, 2)
        if self.range > self.maxRange:
            self.range = self.maxRange
        if self.range < self.minRange:
            self.range = self.minRange


class Sonar(Sensor):
    def __init__(self, index, minRange, maxRange):
        Sensor.__init__(self, 'sonar', index, minRange, maxRange)
        self.index = index
        print("new Sonar" + repr(self.index))

    def initialize(self):
        Sensor.initialize(self)
        # do something specific to Sonar
        self.range = (self.minRange + self.maxRange)/2  # initialize to half range

    def makeMeasurment(self):
        self.range = self.range + random.randint(-1, 1)
        if self.range > self.maxRange:
            self.range = self.maxRange
        if self.range < self.minRange:
            self.range = self.minRange


class Switch(Sensor):
    def __init__(self, index,  minRange, maxRange):
        Sensor.__init__(self, 'switch', index,  minRange, maxRange)
        self.index = index
        print("new Switch" + repr(self.index))

    def initialize(self):
        Sensor.initialize(self)
        # do something specific to Switch
        self.range = 0

    def makeMeasurment(self):
        if random.randint(0, 1000) == 1000:        # SIMU:  0.1% chance to get a switch ON...
            self.range = 1
        else:
            self.range = 0


if __name__ == "__main__":
    random.seed()
    meas = 0
    dist = 0
    nbOfSonars = 0
    cpt = 0

    sar = []
    dar = []
    car = []

    currentState = StateMachine.init
    ax1 = plt.subplot()
    ax2 = ax1.twinx()

    color1 = 'blue'
    ax1.set_ylabel('speed', color=color1)
    # plt.ylim(0, 50)

    color2 = 'green'
    ax2.set_ylabel('dist', color=color2)

    plt.ion()

    def backspace(n):
        print('\r', end='')

    while 1:

        if currentState == StateMachine.init:
            speed = 0

            # get system configuration from json file
            current_file_path = __file__
            current_file_dir = os.path.dirname(__file__)
            sensors_file_path = os.path.join(current_file_dir, "sensors.json")
            with open(sensors_file_path) as json_file:
                json_data = json.load(json_file)

            # create the sensors
            index = 0
            _switch = json_data.get('Switch')
            for i in range(_switch.get('Number')):
                sensorsList.append(Switch(i, _switch.get('MinRange'), _switch.get('MaxRange')))
                index += 1

            index = 0
            _lidar = json_data.get('Lidar')
            for i in range(_lidar.get('Number')):
                sensorsList.append(Lidar(i, _lidar.get('MinRange'), _lidar.get('MaxRange')))
                if max_speed > _lidar.get('MaxRange'):
                    plt.ylim(0, max_speed)
                else:
                    plt.ylim(0, _lidar.get('MaxRange'))
                break  # max 1 lidar

            index = 0
            _sonar = json_data.get('Sonar')
            for i in range(_sonar.get('Number')):
                sensorsList.append(Sonar(i, _sonar.get('MinRange'), _sonar.get('MaxRange')))
                index += 1
                nbOfSonars += 1
            print()

            # initialize sensors
            for s in sensorsList:
                s.initialize()
                print(s.type + repr(s.index) + ": state " + stateArray[s.state.value])
            print()

            # run Lidar (if any) and switch
            for s in sensorsList:
                if s.type == 'lidar' or s.type == 'switch':
                    s.run()
                else:
                    s.sleep()
                print(s.type + repr(s.index) + ": state " + stateArray[s.state.value])
            print()
            currentState = StateMachine.checkSensors

        elif currentState == StateMachine.checkSensors:
            # check running sensors measurments
            dist = 0
            for s in sensorsList:
                if s.type == 'switch' and s.state == State.running:
                    s.makeMeasurment()
                    if s.range == 1:
                        print("STOP: switch detected !")
                        print()
                        currentState = StateMachine.Stop
                        break

                if s.type == 'lidar' and s.state == State.running:
                    s.makeMeasurment()
                    dist = s.range

                    # if lidar minRange, we switch to Sonar, keep hysteresis between sonar and lidar!
                    # switch to sonar when dist = minRange
                    if dist == s.minRange:
                        for s in sensorsList:
                            if s.type == 'lidar':
                                s.stop()
                            if s.type == 'sonar':
                                print("Switch to Sonar")
                                s.run()
                                s.range = dist  # sonar start with same measurmnent as lidar...
                        break

                    if dist < 2:
                        currentState = StateMachine.Stop
                    elif dist < 5:
                        currentState = StateMachine.slowDown
                    elif (dist/(speed+1)) > 1:
                        currentState = StateMachine.speedUp
                    else:
                        currentState = StateMachine.slowDown

                if s.type == 'sonar' and s.state == State.running:
                    s.makeMeasurment()
                    dist += s.range

                    if s.index == nbOfSonars-1:
                        dist /= nbOfSonars  # average of sonars...

                        # switch to lidar when dist = maxRange
                        if dist == s.maxRange:
                            for s in sensorsList:
                                if s.type == 'sonar':
                                    s.stop()
                                if s.type == 'lidar':
                                    print("Switch to Lidar")
                                    s.run()
                                    s.range = dist  # lidar start with same measurmnent as sonar...
                            break

                        if dist < 1:
                            currentState = StateMachine.Stop
                        elif dist < 2:
                            currentState = StateMachine.slowDown
                        elif speed < dist:
                            currentState = StateMachine.speedUp
                        else:
                            currentState = StateMachine.slowDown

        elif currentState == StateMachine.speedUp:
            if speed < max_speed:
                speed += 1
            currentState = StateMachine.checkSensors

        elif currentState == StateMachine.slowDown:
            if speed > 1:
                speed -= 2
            currentState = StateMachine.checkSensors

        elif currentState == StateMachine.Stop:
            speed = 0
            currentState = StateMachine.checkSensors

        if currentState != StateMachine.checkSensors:
            s = 'distance = ' + repr(dist) + "  -> " + smArray[currentState.value] + " -- speed = " + repr(speed) + "           "
            print(s, end='')
            backspace(len(s))

            sar.append(speed)
            dar.append(dist)
            car.append(cpt)

            ax1.plot(car, sar, lw=1, color='b')
            ax2.plot(car, dar, lw=1, color='g')

            plt.pause(0.01)
            plt.draw()
            # plt.show()
            cpt += 1

        # time.sleep(0.1)
