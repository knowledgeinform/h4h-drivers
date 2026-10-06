# Copyright Endeavor Robotics 2016. Unpublished --
# Rights Reserved Under the Copyright Laws of the United States.
# Any Reproduction or Dissemination of this Copy is Strictly Prohibited.
# U.S. Gov't employees should consider this file a trade secret
# under 18 USC 1905. Contact Endeavor Robotics for details.
#
# COMMERCIAL ITEM
# The technical data and computer software contained/transmitted herein is
# proprietary to Endeavor Robotics, is Endeavor Robotics' commercial
# technical data and commercial computer software and computer software
# documentation, and may not be used, disclosed, reproduced, modified,
# performed, or displayed except as permitted by Endeavor Robotics'
# standard commercial license for this Data or computer software. United
# States Government license rights are limited to those rights set forth
# in Endeavor Robotics' standard commercial license.

## Supported behaviors

# True if movement can be stopped when an obstacle is detected
bool support_stop_on_obstacle

# True if movement can plan around an obstacle when an obstacle is detected
bool support_avoid_obstacle


## Configuration data

# Enums for state values
uint8 DO_NOTHING = 0
uint8 STOP_ON_PATH = 1
uint8 DEVIATE_FROM_PATH_TO_AVOID_COLLISIONS = 2

# The current collision avoidance state
uint8 state

# The collision avoidance priority
uint8 priority


## Status data

# Enum status values
uint8 DISABLED = 0
uint8 ENABLED = 1
uint8 ACTIVE_STOP_ON_OBSTACLE = 2
uint8 ACTIVE_AVOID_OBSTACLE = 3

# The current collision avoidance status
uint8 status
