# RFID Proxy

## Overview
This is a very simple TCP Proxy that will proxy *RaceDB* LLRP RFID reader commands to a *Impinj Speedway Revolution* RFID reader
via the QLMUX Proxy.

This is done to allow *RaceDB* to have a static configuration for the RFID reader.

The actual RFID Reader is found using SNMP, and the configuration used can be changed interactively
via the QLMUX web status page.

This not needed if only a single instance of *RaceDB* is running, as the RFID reader can be configured
to the default 5084 port.

Additional instances need to use different ports. E.g. 5085, 5086, etc.

## Operation

The RFID Proxy listens on a port (default 5084) for incoming connections from *RaceDB*. 
When a connection is accepted it connects to the proxy host and port (default qlmuxproxy.local:5085)
and the proxies the data between the two connections.

The QLMUX Proxy listens on a limited number of ports, typically 5084, 5085, 5086, etc. It accepts
connections on those ports. When a connection is accepted it connects to the RFID Reader that has
been found via SNMP and proxies the data between the two connections.
```
+-----------------+        +-----------------+                                   +-----------------+
| RaceDB          |<------>| RFID Proxy      |<---------\            /---------->| RFID Reader     |
+-----------------+        +-----------------+        +-----------------+        +-----------------+
                                                      | QLMUX Proxy     |
+-----------------+        +-----------------+        +-----------------|        +-----------------+
| RaceDB          |<------>| RFID Proxy      |<---------/            \---------->| RFID Reader     |
+-----------------+        +-----------------+                                   +-----------------+

```

## Installation
Typically this will be installed into the RaceDB image so that it is available for use in the container.

## Configuration
See the rfidproxy.env file.

Typically:
```
RFID_PROXY_HOST=qlmuxproxy.local
RFID_PROXY_PORT=5085
```

N.b. the qlmuxproxy.local must be the name specified for use in the QLMUX Proxy container.

