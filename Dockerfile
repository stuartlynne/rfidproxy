


FROM alpine:latest

# update and get extra utilities
#RUN apt-get update && apt-get install -y vim less psmisc netcat-openbsd telnet pdftk poppler dos2unix
RUN apk add --no-cache vim git less poppler dos2unix openssh

ENV TIME_ZONE=America/Vancouver

# clone qllabels into /
RUN cd / && git clone https://github.com/stuartlynne/qllabels.git 
RUN cp /qllabels/bin/QLLABELS.py /usr/local/bin
RUN adduser -D racedb
RUN ssh-keygen -q -N "" -t rsa -b 1024 -f /etc/ssh/ssh_host_rsa_key

ENTRYPOINT ["/usr/sbin/sshd", "-D", "-o", "PermitEmptyPasswords=yes"]

