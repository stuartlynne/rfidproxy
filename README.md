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

This script will install QLLABELS.py and required libraries into a RaceDB container.

QLLABELS.py implements support for RaceDB printing Frame numbers and Bib numers using
Brother QL style network label printers, e.g.:

      QL-710w - frame, shoulder, emergency contact
      QL-1060N - bib numbers

Run this script in the RaceDB/docker directory to install the qllabels git archive
into the racedb container after creating the racedb container (typically after
using ./racedb run).

Running this script will install /home/RaceDB/scripts/QLLABELS.py and required
support packages pdf2image, poppler-utils and brother_ql

QLLABELS.py usage:

In the RaceDB System Info Edit screen:

  Cmd used to print Bib Tag (parameter is PDF file)

      [  /home/RaceDB/scripts/QLLABELS $1 ]


QLLABELS uses the following to convert the PDF file to Brother Raster format and
sends that to a target host and port.

      pdf2image is used to convert PDF to PNG
      brother_ql is used to convert PNG to Brother Raster

The QLLABELS.py script can be customized to send the resulting raster files to
either a local (pair) of printers (hostname or ip address):

      size    hostname        port
      small   ql710w          9100
      large   ql1060n         9100

Alternately if the qlmuxd program is installed in another container it can be used.

Direct access to the printers is only suitable for low use, i.e. one registration
operator. Multiple operators issuing over lapping print jobs will result in bad 
labels being printed. The qlmuxd program implements printer pools for small and 
large printers with fail over support and prevents over lapping requests. This
allows multiple operators to issue print requests and have the labels printed
at a specific printer.

A common configuration used by four operators:

| Operator |  Large  | Backup  | Small   | Backup  |
|:--------:|:-------:|:-------:|:-------:|:-------:|
| antenna1 | ql10601 | ql10602 | ql710w1 | ql710w3 |
| antenna2 | ql10601 | ql10602 | ql710w1 | ql710w3 |
| antenna3 | ql10602 | ql10601 | ql710w2 | ql710w3 |
| antenna4 | ql10602 | ql10601 | ql710w2 | ql710w3 |

Sample host file:

| IP Address    | Hostname |
|:--------------|:--------:|
| 192.168.40.41 | ql710w1  |
| 192.168.40.42 | ql710w2  |
| 192.168.40.43 | ql710w3  |
| 192.168.40.44 | ql1060n1 |
| 192.168.40.45 | ql1060n2 |

Each pair of operators (1/2 and 3/4) had two printers (one of each size)
dedicated to them. A third ql710w printer in the middle acts as a backup 
for the two small printers on each side. Each of the large printers acts
as a backup for the other.

