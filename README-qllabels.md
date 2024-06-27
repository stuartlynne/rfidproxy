# qllabels
## Fri Aug 13 13:54:46 PDT 2021

This implements *qllabels.py*, a script for *RaceDB* can use to print labels to
*Brother* *QL* style network label printers.

This script will convert the PDF file to Brother Raster file(s) and
send the Raster file(s) to a Brother QL style label printer or to
the [*qlmux\_proxy*](https://github.com/stuartlynne/qlmux_proxy) printer spooler.

*qllabels* and *qlmux_proxy* will print labels
far faster than *CUPS* using the standard Brother QL support files.
Typical imaging and data transfer times to the printer are between
1-2 seconds.

The qlmux\_proxy program manages pools of QL printers and will spool
the data allowing multiple people to print to them, with support
for different printers for the different antennas and fall-over
support if (when) the printers are not available (typically when
they run out of labels. The qlmux\_proxy program takes the same raster
file data that would be sent to the printers on port 9100, but
uses ports 910N to allow us to specify which pool of printers
to use.

This script will:

- convert the PDF data on <STDIN> into an image
- convert the image into Brother Raster Data
- send the raster data to one of four TCP ports 9101, 9102, 9103, 9104

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

| RFID | Target | Size | Type |
| -- | -- | -- | -- |
| 1 | 9101 | 2"x4" | Frame/Shoulder |
| 2 | 9102 | 2"x4" | Frame/Shoulder |
| 3 | 9103 | 4"x6" | Bib |
| 4 | 9104 | 4"x6" | Bib |


## RaceDB

qllabels.py setup in RaceDB.

There are two ways to use qllabels.py.

### Direct Instal
It can be installed in the RaceDB container and 
used directly. The qllabels.py script will connect to ports 9101-9104 to send data.
This assumes that the qlmux_proxy container is running to accept the data.

'''
  Cmd used to print Bib Tag (parameter is PDF file)

      [ qlabels.py $1 ]
'''

### Using SSH
It can be accessed via ssh in the qlmux_proxy container. This is slightly less efficient
because the data needs to be transferred via ssh into the second container before 
being processed.

In the RaceDB System Info Edit screen one of the following:

'''
  Cmd used to print Bib Tag (parameter is PDF file)

      [  ssh -o StrictHostKeyChecking=no qlmux_proxu.local qlabels.py $1 ]
'''

N.b. StrictHostKeyChecking will keep ssh from complaining about the *qlmux_proxy.local* host
key. That gets changed when the image is rebuilt, and if this is not used then an interactive
connection would be required to allow the current key to be added to the list of known hosts.


## [Related Projects](related.md)


