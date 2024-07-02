#!/usr/bin/python3
# 
# rfidproxy.py
# stuart.lynne@gmail.com
# 
# Listen on a set of ports, 1-4
#   127.0.0.N:5084
#
# Proxy to a set of ports:
#   0.0.0.0:5085+N
#
import os
import socket
import select
import time
import sys
import platform
from threading import Thread, Event
from queue import Queue
import traceback
import signal
from dotenv import load_dotenv

from jaraco.docker import is_docker

import sys
import datetime
getTimeNow = datetime.datetime.now


def log(s):
    print('%s %s' % (getTimeNow().strftime('%H:%M:%S'), s.rstrip()), file=sys.stderr)

def set_keepalive_linux(sock, after_idle_sec, interval_sec, max_fails):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

def set_keepalive_osx(sock, after_idle_sec, interval_sec, max_fails):
    """Set TCP keepalive on an open socket.

    sends a keepalive ping once every 3 seconds (interval_sec)
    """
    # scraped from /usr/include, not exported by python's socket module
    TCP_KEEPALIVE = 0x10
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)

def set_keepalive_win(sock, after_idle_sec, interval_sec, max_fails):
    sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, after_idle_sec * 1000, interval_sec * 1000))


def set_keepalive(sock, after_idle_sec=60, interval_sec=60, max_fails=5):
    plat = platform.system()
    if plat == 'Linux':
        return set_keepalive_linux(sock, after_idle_sec, interval_sec, max_fails)
    if plat == 'Darwin':
        return set_keepalive_osx(sock, after_idle_sec, interval_sec, max_fails)
    if plat == 'Windows':
        return set_keepalive_win(sock, after_idle_sec, interval_sec, max_fails)
    raise RuntimeError('Unsupport platform {}'.format(plat))

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_keepalive(self.forward, after_idle_sec=4, interval_sec=1, max_fails=3)
        self.forward.settimeout(5)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            log('Forward.start: Exception: %s' % (e,), )
            return None

class TCPProxy(Thread):

    def __init__(self, listen_address='127.0.0.1', listen_port=None, proxy_address=None, proxy_port=None, stopEvent=None, changeEvent=None, tcpStatusQueue=None, loopback=False):
        super(TCPProxy, self).__init__()
        self.input_list = []
        self.channel = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_keepalive(self.server, after_idle_sec=4, interval_sec=1, max_fails=3)
        self.server.settimeout(5)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        log('bind: %s:%s' % ( listen_address, listen_port))
        self.server.bind((listen_address, listen_port))
        self.server.listen(200)
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.stopEvent = stopEvent
        self.changeEvent = changeEvent
        self.tcpStatusQueue = tcpStatusQueue
        self.loopback = loopback
        log('TCPProxy.__init__[%s:%s] proxy_port: %s loopback: %s' % (self.listen_address, self.proxy_address, self.proxy_port, self.loopback), )

        self.dataReceived = 0
        self.messagesReceived = 0

    def update(self, tcpStatus):
        log('TCPProxy.update[%s] %s' % (self.proxy_address, tcpStatus,), )
        if self.tcpStatusQueue:
            self.tcpStatusQueue.put({self.proxy_address: tcpStatus})

    def close_all(self):
        log('TCPProxy.close_all[%s]' % (self.proxy_address), )
        for k, v in self.channels.items():
            v.close()
        self.channels = {}
        self.input_list = [self.server]

    def run(self):
        self.input_list = [self.server]
        self.channels = {}
        # run until stopEvent is set
        try:
            while not self.stopEvent.is_set():
                inputready, outputready, exceptready = select.select(self.input_list, [], [], 2)

                # if stopEvent is set, close all proxied connections 
                if self.stopEvent.is_set():
                    log('TCPProxy.run[%s]: changeEvent is set' % (self.proxy_address), )
                    self.close_all()
                    #for k, v in self.channels.items():
                    #    v.close()
                    #self.channels = {}
                    #self.input_list = [self.server]
                    continue

                # normal operation, process received data 
                for s in inputready:

                    # New connection
                    if s == self.server:
                        self.on_accept()
                        log('TCPProxy.run[%s]: accepted' % (self.proxy_address), )
                        self.update({'status': 'connected'})
                        break

                    # Incoming data to be forwarded
                    try:
                        data = s.recv(4096)
                    except OSError as e:
                        log('TCPProxy.run[%s]: OSError %s' % (self.proxy_address, e), )
                        data = b''
                    except ConnectionResetError as e:
                        log('TCPProxy.run[%s]: ConnectionResetError %s' % (self.proxy_address, e), )
                        data = b''

                    # No data means the connection is closed
                    if len(data):
                        if self.loopback:
                            self.dataReceived += len(data)
                            self.messagesReceived += 1
                            self.update({'dataReceived': self.dataReceived, 'messagesReceived': self.messagesReceived})
                            s.send(data)
                        else:
                            self.dataReceived += len(data)
                            self.messagesReceived += 1
                            self.update({'dataReceived': self.dataReceived, 'messagesReceived': self.messagesReceived})
                            self.channels[s].send(data)
                        continue

                    log('TCPProxy.run[%s]: has disconnected' % (self.proxy_address, ), )
                    try:
                        if s in self.channels:
                            for c in [s, self.channels[s]]:
                                if c in self.input_list:
                                    self.input_list.remove(c)
                                self.update({'status': 'disconnected'})
                                c.close()
                                if c in self.channels:
                                    del self.channels[c]
                    except KeyError as e:
                        log('TCPProxy.run[%s]: KeyError %s' % (self.proxy_address, e), )
                        log(traceback.format_exc(), )

        except Exception as e:
            log('TCPProxy.run[%s]: Exception %s' % (self.proxy_address, e), )
            log(traceback.format_exc(), )
        log('TCPProxy.run[%s]: stopEvent is set' % (self.proxy_address), )


    def on_accept(self):
        clientsock, clientaddr = self.server.accept()
        log('TCPProxy.on_accept[%s] has connected %s proxy_port: %s loopback: %s' % (self.proxy_address, (clientaddr), self.proxy_port, self.loopback, ), )
        if not self.proxy_address:
            log('TCPProxy.on_accept[%s] has connected, but no proxy_address' % (clientaddr,), )
            clientsock.close()
            return
        set_keepalive(clientsock, after_idle_sec=4, interval_sec=1, max_fails=3)
        clientsock.settimeout(5)
        if self.loopback:
            #self.channels[clientsock] = clientsock  
            self.input_list.append(clientsock)
            self.channels[clientsock] = clientsock
            return
        forward = Forward()
        # XXX this needs to be done asynchronously
        s = Forward().start(self.proxy_address, self.proxy_port)

        if s:
            log('TCPProxy.on_accept[%s] proxied from %s' % (self.proxy_address, clientaddr, ), )
            self.input_list.append(clientsock)
            self.input_list.append(s)
            self.channels[clientsock] = s
            self.channels[s] = clientsock
        else:
            log("TCPProxy.on_accept[%s] Can't establish connection with remote server." % (self.proxy_address), )
            log("TCPProxy.on_accept[%s] Closing connection with client side %s" % (self.proxy_address, clientaddr), )
            clientsock.close()

def main():

    # Need to connect to the host IP address, not the docker container IP address
    # if running in a docker container. 
    if is_docker():
        proxy_address = '172.17.0.1'
    else:
        proxy_address = '0.0.0.0'
    log('proxy_address: %s' % (proxy_address,), )

    loopback = len(sys.argv) == 2 and sys.argv[1] == '-l'
    if loopback:
        log('loopback: %s' % (loopback,), )

    stopEvent = Event()
    changeEvent = Event()

    # XXX - need to add a way to override this
    # 172.17.0.1 is the docker host, apparently hard coded
    # Could also use this in the startup script. See default via 172.NN.0.1 dev eth0
    #    ip r
    #    default via 172.27.0.1 dev eth0 
    #    172.27.0.0/16 dev eth0 scope link  src 172.27.0.3 
    servers = [
        TCPProxy(stopEvent=stopEvent, changeEvent=changeEvent, 
                 listen_address='127.0.0.%d' % i, listen_port=5084, 
                 proxy_address=proxy_address, proxy_port=5084+i, loopback=loopback) 
            for i in range(1, 4)]

    def sigintHandler(signal, frame):
        log('SIGINT received %s, setting stopEvent' % (signal,), )
        stopEvent.set()
        changeEvent.set()
  
    signal.signal(signal.SIGINT, lambda signal, frame: sigintHandler(signal, frame))

    log('starting server', )
    #server.start()
    for server in servers:
        server.start()
    log('server started, waiting', )
    stopEvent.wait()
    log('server stopping, joining', )
    for server in servers:
        server.join()
    log('server stopped', )


if __name__ == '__main__':
    main()


