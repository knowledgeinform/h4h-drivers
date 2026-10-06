# A replication of iop_msgs/SelfCollisionAvoidanceConfiguration
# State Enums
uint8 DO_NOTHING=0
uint8 STOP_ON_PATH=1
uint8 DEVIATE_FROM_PATH_TO_AVOID_COLLISIONS=2

# Status enums
uint8 DISABLED=0
uint8 ENABLED=1
uint8 ACTIVE_STOP_ON_OBSTACLE=2
uint8 ACTIVE_AVOID_OBSTACLE=3

# Actual Vars
bool support_stop_on_obstacle
bool support_avoid_obstacle
uint8 state
uint8 priority
uint8 status


#ubuntu@er-mbu:~$ rostopic echo /kamino/collision_avoidance/state
#support_stop_on_obstacle: True
#support_avoid_obstacle: False
#state: 1
#priority: 0
#status: 1
