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


```
Network Internal to docker-compose environment

           +-----------------------------------------------------+
           | RaceDB                                              |
           | ssh -J qllabels.local /usr/local/bin/QLLABELS.py $1 |
           + ----------------------------------------------------+
               | 
               v 
           +- 22 ---------------------------+
           | sshd                           |
           | QLLABELS.sh print_file         |
           +--------------------------------+
               |        |        |        |
               v        v        v        v 
           +- 9101 ----9102 ----9103 ----9103 -------------------+
           | qlmuxd                                              |
           + ----------------------------------------------------+
 . . . . . . . | . . . . . | . . . . . | . . . . . | . . . . . | . . . . . .
               v           v           v           v           v
           +- 9100 --+ +- 9100 --+ +- 9100 --+ +- 9100 ---+ +-9100-----+ 
           | ql710w1 | | ql710w2 | | ql710w3 | | ql1060n1 | | ql1060n2 |
           +---------+ +---------+ +---------+ +----------+ +----------+ 

Network Outside of docker-compose environment

```





```
