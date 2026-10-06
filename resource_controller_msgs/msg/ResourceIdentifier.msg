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

# The name of the resource
string name

# The topic where the resource's state value is published
string get_state_topic

# The topic where commands to the resource should be published
string send_command_topic

# The topic where most recent arbitrated command sent to the resource is published
string get_command_topic

# The type of the resource
resource_controller_msgs/ResourceType type