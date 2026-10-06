# Platform Port Numbering Scheme
Control Port (controlMessage: UCC --> KxM (h4h))  
Status Port (statusMessage: platform --> UCC)

| Platform 1        | rlac_c100 |
| --------          | ------- |
| Control Port      | 5551    |
| Status Port       | 5561    |

| Platform 2        | rlac_teal |
| --------          | ------- |
| Control Port      | 5552    |
| Status Port       | 5562    |

| Platform 3        | mtrs_chassis |
| --------          | ------- |
| Control Port      | 5553    |
| Status Port       | 5563    |

| Platform 4        | mtrs_gripper |
| --------          | ------- |
| Control Port      | 5554    |
| Status Port       | 5564    |

| Platform 5        | rlac_v60 |
| --------          | ------- |
| Control Port      | 5555    |
| Status Port       | 5565    |

### Notes 
H4H listens to ports 5556 - 5559 for all control messages and parses them according to the `<name>` tag on each message. 