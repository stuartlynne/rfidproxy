# qllabels
# Fri Mar  1 09:30:06 AM PST 2024
# Fri Aug 13 13:54:46 PDT 2021

This implements *qllabels.py*, a script for *RaceDB* can use to print labels to
*Brother* *QL* style network label printers.

This script will convert the PDF file to Brother Raster file(s) and
send the Raster file(s) to a Brother QL style label printer or to
the qlmuxd printer spooler.

The qlmuxd program manages pools of QL printers and will spool
the data allowing multiple people to print to them, with support
for different printers for the different antennas and fall-over
support if (when) the printers are not available (typically when
they run out of labels. The qlmuxd program takes the same raster
file data that would be sent to the printers on port 9100, but
uses ports 910N to allow us to specify which pool of printers
to use.

This script will print labels
faster than CUPS using the standard Brother QL support files.
Typical imaging and data transfer times are under a half second.

This script will:

- convert the PDF data on <STDIN> into a an image
- convert the image into Brother Raster Data
- send the raster data to one of four ports 9101, 9102, 9103, 9104

The argument provided is the file name which contains information about what is to
be printed. E.g.:
```
      230489203498023809\_bib-356\_port-8000\_antenna-2\_type-Frame.pdf
```
- "type" is one of Frame, Body, Shoulder or Emergency.
- "port" is the RaceDB RFID server port.
- "antenna" is the antenna of the user.

The combination of server port and antenna allows different printers to
be used for different registration stations. 

The destination port is determined by the RaceDB RFID server port

| RFID | Target | Size | Type }
| -- | -- | -- | -- |
| 1 | 9101 | 2"x4" | Frame/Shoulder |
| 2 | 9102 | 2"x4" | Frame/Shoulder |
| 3 | 9103 | 4"x6" | Bib |
| 4 | 9104 | 4"x6" | Bib |


## RaceDB

qllabels.py setup in RaceDB.

There are two ways to use qllabels.py.

1. It can be installed in the RaceDB container and 
used directly. The qllabels.py script will connect to ports 9101-9104 to send data.
This assumes that the qlmux_proxy container is running to accept the data.

2. It can be accessed via ssh in the qlmux_proxy container. This is slightly less efficient
as the data needs to be copied via ssh into the second container and then processed.

In the RaceDB System Info Edit screen one of the following:

1. direct install
'''
  Cmd used to print Bib Tag (parameter is PDF file)

      [ qlabels.py $1 ]
'''
2. ssh
'''
  Cmd used to print Bib Tag (parameter is PDF file)

      [  ssh -o StrictHostKeyChecking=no qlmux_proxu.local qlabels.py $1 ]
'''

N.b. StrictHostKeyChecking will keep ssh from complaining about the *qlmux_proxy.local* host
key. That gets changed when the image is rebuilt, and if this is not used then an interactive
connection would be required to allow the current key to be added to the list of known hosts.

Alternately if the qlmuxd program is installed in another container it can be used.

Direct access to the printers is only suitable for low use, i.e. one registration
operator. Multiple operators issuing over lapping print jobs will result in bad 
labels being printed. The qlmuxd program implements printer pools for small and 
large printers with fail over support and prevents over lapping requests. This
allows multiple operators to issue print requests and have the labels printed
at a specific printer.

## Related Github Archvies
| Description | GitHub Archive |
| -- | -- |
|qlmux\_proxy | https://github.com/stuartlynne/qlmux_proxy|
|qllabels | https://github.com/stuartlynne/qllabels/|
|traefik\_racedb | https://github.com/stuartlynne/traefik_racedb|
|racedb\_qlmux | https://github.com/stuartlynne/racedb_qlmux|
|wimsey\_timing | https://github.com/stuartlynne/wimsey_timing|
  



