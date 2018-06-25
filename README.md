# This project SENSORS simulate create an dsimulate a list of sensors:
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
# The main loop state machine start with creating and initialiszinf the sensors according
# to the parameters of the json file  the according to the distance measured we Speed up or Slow down
# Speed is set to zero if deistance is under 1m
#
#
# Tested with Python 3.4.3 and matplotlib 2.2.2

