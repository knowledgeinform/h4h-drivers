cmake_minimum_required(VERSION 2.8.3)
project(resource_controller_msgs)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  message_generation
  roscpp
  rospy
  std_msgs
)
include_directories(${catkin_INCLUDE_DIRS})
link_directories(${catkin_LIBRARY_DIRS})


############################################################
# Define messages and services
#

#### Add all messages
add_message_files(
  FILES
  AxisCommand.msg
  AxisState.msg
  BoolCommand.msg
  CommandHeader.msg
  CommsLossState.msg
  Int32Command.msg
  Float32Command.msg
  Float64Command.msg
  ResourceIdentifier.msg
  ResourceType.msg
  MTRSCollisionAvoidance.msg
)

#### Add all services
add_service_files(
  FILES
  FindResources.srv
  RegisterResources.srv
  UnregisterResources.srv
)

#### Generate source for all messages and services
generate_messages(
  DEPENDENCIES
  std_msgs
)


###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package()


############################################################
# Define tests
#

#if(CATKIN_ENABLE_TESTING)
#  catkin_add_gtest(resource_controller_message_tests test/resource_controller_message_tests.cpp)
#  target_link_libraries(resource_controller_message_tests ${LIBS})
#endif()
