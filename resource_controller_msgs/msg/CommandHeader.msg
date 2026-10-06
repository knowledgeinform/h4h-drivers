# Copyright Endeavor Robotics 2018. Unpublished --
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

# Priority for the command
# Commands with higher priorities take precedence over
# commands with lower priorities
int32 priority

# True if this is a valid command, false is the equivalent of no command
bool valid

# The time at which this command originated
time timestamp

# Number of seconds for which this command remains valid
float32 lifespan_secs

# Lifespan value for command to never time out
float32 LIVE_FOREVER = -1