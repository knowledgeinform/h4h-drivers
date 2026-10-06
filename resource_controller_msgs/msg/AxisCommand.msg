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

# The header for the command
resource_controller_msgs/CommandHeader header

# The type of command
uint8 type

# An invalid command
uint8 INVALID = 0

# An effort command
uint8 EFFORT = 1

# A position command
uint8 POSITION = 2

# A velocity command
uint8 VELOCITY = 3

# A torque command
uint8 TORQUE = 4

# The actual command value
float64 command