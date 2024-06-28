# RFID Proxy

## Overview
This is a very simple TCP Proxy that will proxy *RaceDB* LLRP RFID reader commands to a *Impinj Speedway Revolution* RFID reader
via the QLMUX Proxy.

This is done to allow *RaceDB* to have a static configuration for the RFID reader.

RFID Proxy listens to port 5084 on multiple IP addresses (127.0.0.N for N=1..3) and proxies the data to the QLMUX Proxy
at 0.0.0.0:5084+N.

This allows multiple instances of *RaceDB* to connect to the multiple RFID readers that are in turn
discovered and selected using SNMP in QLMUX Proxy.


## Operation

The RFID Proxy listens on a port (default 5084) for incoming connections from *RaceDB*. 
When a connection is accepted it connects to the proxy host and port (default qlmuxproxy.local:5085)
and the proxies the data between the two connections.

The QLMUX Proxy listens on a limited number of ports, typically 5084, 5085, 5086, etc. It accepts
connections on those ports. When a connection is accepted it connects to the RFID Reader that has
been found via SNMP and proxies the data between the two connections.
```
  +------------------------------------------------+  +----------------------+
  |RaceDB Container                                |  |QLMux Container       |
  | +-----------------+        +-----------------+ |  |  +-----------------+ |     +-----------------+
  | | RaceDB          |        | RFID Proxy      | |  |  | QLMUX Proxy     | |     | RFID Reader     |
  | | 127.0.0.1:5084  |<------>| 127.0.0.1:5084  |<----->| 0.0.0.0:5085    |<----->| n.n.n.n:5084    |
  | +-----------------+        |                 | |  |  |                 | |     +-----------------+
  | +-----------------+        |                 | |  |  |                 | |     +-----------------+      
  | | RaceDB          |        |                 | |  |  |                 | |     | RFID Reader     |      
  | | 127.0.0.1:5084  |<------>| 127.0.0.1:5084  |<----->| 0.0.0.0:5086    |<----->| n.n.n.n:5084    |      
  | +-----------------+        +-----------------+ |  |  +-----------------+ |     +-----------------+       
  |                                                |  |                      |     +-----------------+
  +------------------------------------------------+  +----------------------+
```

## Installation
Typically this will be installed into the RaceDB image so that it is available for use in the container.

Each instance of RaceDB will need to have this set in their environment variables to connect to the correct RFID Reader,
where N is the number of the RFID Reader (1..3). This must match the selection in the QLMUX Proxy web status page.
```
RFID_READER_HOST=127.0.0.N
```


