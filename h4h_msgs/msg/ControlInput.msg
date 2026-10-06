# Name UID
string name
uint8 priority

## TODO: figure out how to make H4H support non-primitive field types

# linear_x is forward/backwards
float64 linear_x

# linear_z is left/right
float64 linear_y

# linear_z is up/down
float64 linear_z

# angular_x is roll (roll left/right)
float64 angular_x

# angular_y is pitch (pitch forward/backward)
float64 angular_y

# angular_z is yaw (turn left/right)
float64 angular_z

# unique actions
string[] actions
bool[] action_values