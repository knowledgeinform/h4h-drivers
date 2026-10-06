### Explicit enums

### Placeholder default signal
uint8 NOOP = 255

### Soft EStop
uint8 STOP = 0

### 6DOF Movement (Linear/Angular XYZ) ###
# Linear XYZ
uint8 FORWARD_BACKWARD = 1
uint8 RIGHT_LEFT = 2
uint8 UP_DOWN = 3

# Angular XYZ
uint8 ROLL = 4
uint8 PITCH = 5
uint8 YAW = 6

### Abstract enums
# WARNING: SIGNALS [0-6] are already assigned above, so avoid re-using those signals for something else
uint8 SIGNAL_0 = 0
uint8 SIGNAL_1 = 1
uint8 SIGNAL_2 = 2
uint8 SIGNAL_3 = 3
uint8 SIGNAL_4 = 4
uint8 SIGNAL_5 = 5
uint8 SIGNAL_6 = 6
uint8 SIGNAL_7 = 7
uint8 SIGNAL_8 = 8
uint8 SIGNAL_9 = 9
uint8 SIGNAL_10 = 10
uint8 SIGNAL_11 = 11
uint8 SIGNAL_12 = 12
uint8 SIGNAL_13 = 13
uint8 SIGNAL_14 = 14
uint8 SIGNAL_15 = 15
uint8 SIGNAL_16 = 16
uint8 SIGNAL_17 = 17
uint8 SIGNAL_18 = 18
uint8 SIGNAL_19 = 19
uint8 SIGNAL_20 = 20
uint8 SIGNAL_21 = 21
uint8 SIGNAL_22 = 22
uint8 SIGNAL_23 = 23
uint8 SIGNAL_24 = 24
uint8 SIGNAL_25 = 25
uint8 SIGNAL_26 = 26
uint8 SIGNAL_27 = 27
uint8 SIGNAL_28 = 28
uint8 SIGNAL_29 = 29
uint8 SIGNAL_30 = 30


# Message fields
uint8 signal
float64 value

# Special field for passthrough strings describing actions
string passthrough