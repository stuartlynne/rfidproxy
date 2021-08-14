# qllabels
# Fri Aug 13 13:54:46 PDT 2021

This implements *QLLABELS.py*, a script for *RaceDB* can use to print labels to
*Brother* *QL* style network label printers.



This script will convert the PDF file to Brother Raster file(s) and
send the Raster file(s) to a Brother QL style label printer or to
the qlmuxd printer spooler.

Sending the files directly to the printers on port 9100 works, but
only when # there is only a single person using RaceDB. Multiple prints
to a QL printer will result in over lapping labels.

The qlmuxd program manages pools of QL printers and will spool
the data allowing multiple people to print to them, with support
for different printers for the different antennas and fall-over
support if (when) the printers are not available (typically when
they run out of labels. The qlmuxd program takes the same raster
file data that would be sent to the printers on port 9100, but
uses ports 910N to allow us to specify which pool of printers
to use.

This script will get labels printed (either directly or via qlmuxd)
far faster than CUPS using the standard Brother QL support files.

This script will:

1. Convert $1 to $1-$PAGENO.png for each page in the PDF file
2. Convert each page to $1-$PAGENO.rast
3. Equivalent of cat $1-\*.rast | netcat $PRINTER\_HOST $PRINTER\_PORT


The argument provided is the file name which contains information about what is to
be printed. E.g.:
```
      230489203498023809\_bib-356\_port-8000\_antenna-2\_type-Frame.pdf
```
- "type" is one of Frame, Body, Shoulder or Emergency.
- "port" is the RaceDB server port.
- "antenna" is the antenna of the user.

The combination of server port and antenna allows different printers to
be used for different registration stations. The server port refers to
the TCP port that the server responds to, e.g. 8000 or 8001 etc.




For limited (1 person) use QLLABELS.py can

