# Table of Contents
- [Running everything locally](#run-local)
- [Running everything on KxM](#run-kxm)
- [Connecting more radios](#connect-radios)
- [The commons Folder](#commons)
- [Creating a Custom Message](#custom-message) 
- [Changing the Shared Namespace](#shared-namespace) 
- [Full Comms Test on Local Machine](#local-comms) 
- [Installing Docker on the KxM](#install-docker) 
- [Using Simulator with KxM](#simulator-kxm) 
- [Setting up Adafruit GPS](#adafruit-gps) 
- [Notes about the Teal Drone](#teal-drone)
- [Running the PX4 Simulator](#sim-drone)
- [Microhard Radios](#microhard)


## Running everything locally <a name="run-local"></a>

- Get the `h4h-drivers` repo onto your Linux system
- Install Docker
- Edit `docker-compose.yml` and comment/uncomment the services to choose what you want
	- you'll want at least one service from the `Controller Interfaces` section
		- if you're testing with a ZMQ service then you'll want to change `ZMQ_IP` to `127.0.0.1`
	- you'll want at least one service from the `Vehicle Interfaces` section
- update `VERSION.txt` with your branch number
	- i.e. `v1.0_52` for branch issue number 52
- build the Docker containers
	- `./build.sh` 
	- the above will output a list of built images and a list of failed builds
	- for failed images they can be individually built with `./build_images.sh <name-of-image>`
- run the containers
	- `./deploy.sh`


## Running everything on KxM <a name="run-kxm"></a>

- Get the `h4h-drivers` repo onto the KxM
	- ssh into the KxM 
		- `ssh kxm@10.131.6.80` (for kxm1)
		- `ssh kxm@10.131.6.189` (for kxm2)
	- get to the KxM's copy of the repo 
		- `cd jhu/h4h-drivers` (on kxm1)
	- switch to a different branch from the one you're working on
		- `git checkout <branchname>`
	- update `VERSION.txt` with your branch number
		- i.e. `v1.0_52` for branch issue number 52
	- build the Docker containers
		- `./build.sh` 
		- the above will output a list of built images and a list of failed builds
		- for failed images they can be individually built with `./build_images.sh <name-of-image>`
	- run the containers
		- `./deploy.sh`

- Turn on the radios
	- Status Lights:
		- blue:				initializing
		- green + yellow: 	looking for a connection
		- green: 			connected
		- green + red:		low/bad battery 

## Connecting more radios <a name="connect-radios"></a>

- Connect the radio to a computer
	- type in the radio's IP address into a web browser to get to the management GUI
		- if you don't know the radio's IP, use Wireshark to sniff it
	- change the network frequency, bandwdith, and the security key to match

## The `commons` Folder <a name="commons"></a>

This folder houses in-common code that is used by multiple higher level programs. 

- `commons.ros2_lib`
	- contains common ROS2 constructs
- `commons.input_lib`
	- contains code for keyboard input
- `commons.thread_lib`
	- contains common multithreading constructs
- `commons.utils_lib`
	- contains miscellaneous constructs
- `commons.zmq_lib`
	- contains ZMQ pub/sub constructs
- `commons.h4h_lib`
	- contains generic AbstractController base classes


## Creating a Custom Message <a name="custom-message"></a>

- Inside `h4h_msgs/msg` add a new message file "Test.msg"
	- Add your desired fields and names to the message (look at Truck.msg and IceCreamFlavor.msg as examples)
	- Use all lowercase and underscores for variable names
- Update `CMakeLists.xml` with your new message type
	- add you message path to the `rosidl_generate_interfaces` list
- Build the package
	- cd into the `h4h_msgs` folder
	- `colcon build`
	- This will generate three new folders inside `h4h_msgs`
		- build, install, log
- Source the new workspace
	- `source install/setup.bash`
- You are now in a ROS2 workspace (same distro as the one you used to build) that contains the custom messages


## Changing the Shared Namespace <a name="shared-namespace"></a>

- Inside `dockerfiles/h4h_base.dockerfile` at the bottom of the file there's an ENV called ROS_NAMESPACE


## Full Comms Test on Local Machine <a name="local-comms"></a>

- Modify `zmq_ipaddr` in `scripts/ZmqLeftSide.py` to `"127.0.0.1"`
- Swap the commented docker compose lines in `./build_and_deploy.sh` for Docker Compose v2
- run `./build_and_deploy.sh`
- run `docker logs -f --tail 10 h4h-drivers-husky-controller-1` to watch the output
- In another terminal run `python test_zmq_with_keyboard.py`
	- the python dependencies are frozen in `reqs.txt`


## Installing Docker on the KxM <a name="install-docker"></a>

- Install Docker normally following this: `https://docs.docker.com/engine/install/ubuntu/`
	- Use the `Install using the apt repository` section

- Docker Compose v1 can be installed from the repo
	- Go to `https://github.com/docker/compose/releases`
		- note down the version number
		- `sudo curl -L "https://github.com/docker/compose/releases/download/v2.34.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
		- `sudo chmod +x /usr/local/bin/docker-compose`
		- `sudo chown -R $(whoami) ~/.docker`


- Open QGroundControl (double click AppImage file)
- Navigate to PX4-Autopilot folder
	- PX4 simulation can be run with Gazebo visualization using:
		- `make px4_sitl gz_x500`
	- Or without using:
		- `HEADLESS=1 make px4_sitl gz_x500`

## Using Simulator with KxM <a name="simulator-kxm"></a>
- Setting up PX4 Simulator to route ground control to KxM (should only have to do once)
	- run `ifconfig` and determine the network device name for the ethernet connection to radio
	- open PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/px4-rc.mavlink
	- at line 14 (should be a `mavlink start` call), add `-p -n 'NETWORK DEVICE'`

- Setting up Mavros to connect to remote PX4 Simulation
	- On the KxM, in h4h-drivers/resources/params.yaml
		- set `fcu_url = 'udp://<IP OF KxM>:14540@<IP OF HOST>:14557'`

- Running simulation
	- Open QGroundControl (double click AppImage file)
	- In terminal on host computer, navigate to PX4-Autopilot folder
		- PX4 simulation can be run with Gazebo visualization using:
			- `make px4_sitl gz_x500`
		- Or without using:
			- `HEADLESS=1 make px4_sitl gz_x500`
	- In another terminal on host computer, run the following to route mavlink to KxM
		- `mavlink-routerd -e <IP OF KXM>:14540 127.0.0.1:14540`
	- Deploy docker compose on KxM as normal

## Setting up Adafruit GPS <a name="adafruit-gps"></a>
- Connect antenna, GPS module, and host machine. Red LED on Adafruit GPS module will blink at 1Hz after fix is found
- Some steps will be specific to macOS. We forward the port into TCP 5000 as Docker desktop on macOS cannot see /dev/cu.*
- Identify the call-out port (this may change any time you disconnect from the host machine)  
```bash
ls /dev/cu.usbserial-XXX
# e.g. /dev/cu.usbserial-2130
```

- Ensure GPS data is flowing. Each of these are alternative logging methods — Some may work while others will not. Replace XXXX with your serial port number from previous step.
    - using `stty` (preferred since it confirms the GPS is actually sending NMEA, will display logs even without a fix). Look for lines like `$GPGGA,…,1,… (fix) or $GPRMC,…,A,… (valid).`
        ```
        stty -f /dev/cu.usbserial-XXXX 9600 raw -echo 
        cat /dev/cu.usbserial-XXX

    - using screen

        ```screen /dev/cu.usbserial-XXX```

    - using gpsd
        ```
        gpsd -n /dev/cu.usbserial-XXXX -F /tmp/gpsd.sock
        cgps -s
        ```

    - using 'picocom'
        ```
        brew install picocom
        picocom -b 9600 /dev/cu.usbserial-XXX

- TCP forwarding for macOS host debugging (Keep this running while launching Docker)

        brew install socat
        pkill socat || true
        socat \
        TCP-LISTEN:5000,reuseaddr,fork \
        /dev/cu.usbserial-XXX,raw,echo=0
    

    - Verify
    `lsof -iTCP:5000 -sTCP:LISTEN # should show socat listening on port 5000`

- Docker Setup
    - From folder `/scripts/gps_pubishing_test`
        ```
        docker build -t ros2-gps-humble .
    - Run Publisher container
        
        ```
        docker run -d --rm --name gps_node \
        -v "$(pwd)/":/workspace \
        ros2-gps-humble \
        bash -lc "\
            source /opt/ros/humble/setup.bash && \
            python3 /workspace/gps_stream_to_ros.py /dev/ttyGPS 9600 \
            --ros-topic /gps/fix \
            --frame-id gps_link"
        ```
    - /dev/ttyGPS is auto-created by entrypoint.sh
    Script publishes NavSatFix and print JSON to stdout for debugging

    - Check logs
        ```
        docker logs -f gps_node


    - Subscribe or echo /gps/fix
        
        ```
        docker exec -it gps_node bash
        source /opt/ros/humble/setup.bash
        ros2 topic echo /gps/fix
        ```


- If having issues:
    - Ensure all commands use cu.* when referring to the serial port, as tty.* sometimes causes issues
    - Reconnect GPS sensor
    - Consistently ensure GPS data flow using something like:
    ```
    stty -f /dev/cu.usbserial-XXX 9600 raw -echo
    cat /dev/cu.usbserial-XXX
    ``` 
    - Check and kill any processes blocking the port
    ```
    lsof /dev/cu.usbserial-XXX 
    killall gpsd screen picocom || true
    ```
    - Ensure container can open port
        - Host `socat` is running before `docker run`
        - Stop old container: `docker stop gps_node`
    - Check same DDS network across containers
        - exec into container or use `--network container:…`
    - Verify you sourced `setup.bash` and `ros2 topic list` shows `/gps/fix`


## Notes about the Teal Drone <a name="teal-drone"></a>

- Move the Teal drone about 30ft away from the KxM's Microhard radio
	- If it's closer to that it can have really intermittent connection
- Wait for 60 seconds after powering on the drone before connecting to it via USB-C
	- if you connect before then it fails to start up properly for some reason
- The Teal's radio can take as long as 3 minutes from powerup to connect to the KxM's MxC radio
- The drone can be connected to directly via the Android Debug Bridge
	- Get a hardwire connection from your laptop via USB-C and type `adb shell`
	- If you can't connect, check your firewall settings
- The drones are configured via a `configure_eagle_for_kinesis.py` script
	- It's very informal, it might be named slightly differently
	- Inside there are parameters at the top; they are commented correctly so follow those
	- It needs to know the current address of the onboard Microhard radio
		- The only way I've found these is by slowly pinging every `192.168.168.*` address
			- It's probably in the `192.168.168.[30-40]` range
	- We've gotten it to connect to the KxM's MxC radio by setting the Teal to Slave mode and the MxC to Master
		- Mesh mode worked very briefly for a couple of pings and then dropped. More investigation is needed
	- When you run the script it'll use shell commands to auto-type. Don't press anything or you'll screw it up
	- The mavlink router config is under /data/teal/mavlink-router/main.conf
		- UdpEndpoint qgc
			- set Port and Address
	- WARNING: sometimes the Teal doesn't connect to its own radio. This can be confirmed by using adb shell and checking ifconfig.
		- if you don't see the enP1p1s0 link then it has failed to find its own radio. Turn it off, shake it, turn it back on and hope
	- Set a unique sys_id to each system
		- we set the teal to sys_id 2
	- 330832 is the primary TEAL 192.168.168.30, 192.168.168.31 for the radio
	- 329242 is the backup TEAL

	### RTSP Stream URLS 
	* Exact url configuration can be found in `/etc/dcm.conf` on the TEAL  
		* General Structure is 
			* IR Stream: `rtsp://<teal-IP>:<service>/<mapping>`
			* Visible Stream: `rtsp://<teal-IP>:<service>/<mapping>` 
		* `<service>` and `<mapping>` tags can be found in the `[rtsp 640]` settings of the `dcm.conf` file. 
		
	* For the RAD TEAL: 
		* IR Stream: `rtsp://192.168.168.30:8554/video100-klv`
		* Visible Stream: `rtsp://192.168.168.30:8555/video200-klv` 

## Running the PX4 Simulator <a name="sim-drone"></a>

- Build the images
	- `./build.sh`
		- if the base images are failing, check that the time hasn't drifted
		- if it has, you can manually set the time like this:
			- `sudo date -s "Mar 19 14:00"`
			- the `update_time.sh` script sometimes works, but sometimes it's late
- Deploy with the "sim" profile
	- `./deploy.sh sim`
- Wait a few minutes for the PX4 package to build
	- you can watch the logs with `docker logs -f --tail 100 h4h-drivers-h4h-px4-sim-1`
- Open up QGC
	- `flatpak run --device=all org.mavlink.qgroundcontrol`
- Open up the test keyboard controller
	- `source ~/envs/rlac/bin/activate`
	- `python test_zmq_with_keyboard.py`
- Arm the drone and fly
	- "p" to arm
	- "i/k" for up/down
	- "j/l" for straft left/right
	- "w/s" for forward/backward
	- "d/a" for right/left
	- If you land the drone (by hitting zero altitude) then the drone will automatically disarm and will need to be rearmed


## Microhard Radios <a name="microhard"></a>

- KxM's radio is `192.168.168.76`
	- `admin`
	- `micro2326`
- Teal Radio for the `192.168.168.31` drone is `192.168.168.30`
	- `admin`
	- `tealteam`

## Miscellaneous

- The jetson ethernet connection to the kxm sometimes doesn't start up right. Unplugging it on the KxM side and plugging it back in sometimes fixes it
- The V60 Ghost Dog doesn't always connect over the radio if the radio is connected after the V60 is already powered on. Turning the V60 off, plugging in the radio and turning the radio on, then turning on the V60 seems to fix it
- flatpak run --device=all org.mavlink.qgroundcontrol
- GVSC module's wires:
	- two wires going to the ublox gps'
	- yellow ethernet into the switch
	- black ethernet into the switch
	- big black connector into "J2 IOB P 24v" port on the MTRS

## Doodle Lab Radios
Things that must match for our APL C100:
- Firmware: 2024-10.5
- Select Scenario: Mesh on radio0
- Mesh ID: hh8719-c00649
- Wireless Password: !DpCKDFf$Bg@*6M96b
- Channel: 1 (2412 MHz)
- Bandwidth: 20 MHz

## Setting up for the C100
- Set the KxM IP Address to 192.168.168.90
	- edit /etc/netplan/config.yaml
- Set the SROC C100 Controller to 192.168.168.91
- Edit the mavproxy service to output to 192.168.168.91:14550
- The forward camera's video stream address is `rtsp://192.168.168.20:8900/live`
