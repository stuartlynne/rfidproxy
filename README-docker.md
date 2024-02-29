# QLLABELS Containers
#

QLLABELS.py implements converts PDF files sent from RaceDB to Brother Raster data
and forwards that to either:

- standalone Brother QL Printers
- qlmuxd spooler


## Container configuration

- RaceDB 
- qllabels
- qlmux


Typical flow of data between containers:


    RaceDB PDF --> qllabels:22 Raster --> qlmux:910N Raster --> qlXXXX:9100


```
Network Internal to docker-compose environment

           +------------------------------------------+
           | RaceDB                                   |
           | ssh racedb@qllabels.local QLLABELS.py $1 |
           + -----------------------------------------+
           PDF | 
               v 
           +- 22 ----------------------------------+
           | sshd                                  |
           | QLLABELS.py print_file < print_file   |
           +---------------------------------------+
        Raster |        |        |        | 
               v        v        v        v 
           +- 9101 ----9102 ----9103 ----9103 -------------------+
           | qlmuxd                                              |
           + ----------------------------------------------------+
        Raster |           |           |           |           |
 . . . . . . . | . . . . . | . . . . . | . . . . . | . . . . . | . . . . . .
               v           v           v           v           v
           +- 9100 --+ +- 9100 --+ +- 9100 --+ +- 9100 ---+ +-9100-----+ 
           | ql710w1 | | ql710w2 | | ql710w3 | | ql1060n1 | | ql1060n2 |
           +---------+ +---------+ +---------+ +----------+ +----------+ 

Network Outside of docker-compose environment

```





```
