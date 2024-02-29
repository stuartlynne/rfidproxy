


#FROM alpine:latest
FROM frolvlad/alpine-python3:latest

# update and get extra utilities
#RUN apt-get update && apt-get install -y bash vim less psmisc netcat-openbsd telnet pdftk poppler dos2unix
RUN apk add --no-cache bash vim git less busybox-extras netcat-openbsd poppler dos2unix openssh 

ENV TIME_ZONE=America/Vancouver

RUN echo "qllabels.local" > /etc/hostname

# clone qllabels into /
RUN cd / && git clone https://github.com/stuartlynne/qllabels.git 
RUN cp /qllabels/bin/QLLABELS.py /usr/local/bin
RUN adduser -D racedb
RUN passwd -d racedb
#RUN ssh-keygen -q -N "" -t rsa -b 1024 -f /etc/ssh/ssh_host_rsa_key
RUN ssh-keygen -A

ENTRYPOINT ["/usr/sbin/sshd", "-D", "-o", "PermitEmptyPasswords=yes", "-o", "PubkeyAuthentication=no", "-o", "PermitEmptyPasswords=yes", "-o", "PrintMotd=no" ]

