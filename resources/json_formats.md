# JSON Formatting for ZMQ Communication with the UCC

## Control Message 
From UCC --> KxM/H4H (ZMQ) 
* Message can include subset of these, as needed per platform 


```
    {
        "messageType":  "control", 
        "messageData": {
            "name": <string>,
            "linear_x": <float>,
            "linear_y": <float>,
            "linear_z": <float>,
            "angular_z": <float>,

        }
    }
```


## Actions Message 
From UCC --> KxM/H4H (ZMQ) 
* Message can include subset of these, as needed per platform 


```
    {
        "messageType":  "actions", 
        "messageData": {
            "name": <string>,
            "autonomy": <bool>,
            
            <!-- UAV Control  -->
            "arm": <bool>, 
            "disarm": <bool>, 
            <!-- available flight_modes: "MANUAL", "POSITION", "HOLD", "OFFBOARD" -->
            "flight_mode": <string>, 

            <!-- Quadruped Control  -->
            "takeOver": <bool>,
            "sit": <bool>, 
            "stand": <bool>,
            "walk": <bool>,

            <!-- Arm Control  --> 
            "action1": <bool>,
            "action2": <bool>,
            "action3": <bool>,
            "action4": <bool>,
            "action5": <bool>,
            "action6": <bool>,

        }
    }
```


## Status Message 
From Platform (ROS) --> KxM/H4H (ZMQ) --> UCC 

* Message can include subset of these, as needed per platform 


```
    {
        "messageType":  "status", 
        "messageData": {
            "name": <string>,
            "lat": <float>,
            "lon": <float>,
            "alt": <float>,
            "heading": <float>,
            "powerLevel": <float>, 

            <!-- UAV Status  -->
            "flying": <bool>, 
            "landed": <bool>, 
            "flight_mode": <string>,

            <!-- Quadruped Status  -->
            "seated": <bool>, 
            "standing": <bool>, 
            "walking": <bool>

            <!-- Arm Status  -->
            "action1Completed": <bool>, 
            "action2Completed": <bool>, 
            "action3Completed": <bool>, 
            "action4Completed": <bool>, 
            "action5Completed": <bool>, 
            "action6Completed": <bool>, 
        }
    }

```


## Params Message 
From UCC --> KxM (ZMQ) 

```
    {
        "messageType": "params", 
        "messageData": {
            "name": <string>,
            "failsafe": <string>,
            "rtl_altitude": <double>,
            "max_altitude": <double>,
        }
    }
```
