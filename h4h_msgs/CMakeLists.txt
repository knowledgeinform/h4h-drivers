cmake_minimum_required(VERSION 3.5)

# *** Add you package name here ***
project(h4h_msgs)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

# *** if you require any other packages, put them here ***
# Example:
# find_package(geometry_msgs REQUIRED)

find_package(geographic_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# get the message generator
find_package(rosidl_default_generators REQUIRED)

# *** point cmake to your messages here ***
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/IceCreamFlavor.msg"
  "msg/Truck.msg"
  "msg/AbstractSignal.msg"
  "msg/KeyInput.msg"
  "msg/ZmqInput.msg"
  "msg/GeoPoseImage.msg"
  "msg/ControlInput.msg"
  "msg/Vanilla.msg"
  "msg/UAVAltitudeParams.msg"
  "msg/UGVControlInput.msg"
  "msg/BatchedAbstractSignal.msg"
  "msg/H4HHeartbeat.msg"
  DEPENDENCIES geographic_msgs sensor_msgs
 )

ament_export_dependencies(rosidl_default_runtime)

ament_package()
