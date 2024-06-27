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

