#!/usr/bin/env python2
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred
import re

class PingProtocol(protocol.ProcessProtocol):

    def __init__(self, ipaddr):
        self.ipaddr = ipaddr
        self.data = ""
        self.received_re = re.compile("(\d) received")
        self.transmitted_re = re.compile("(\d) packets transmitted")
        self.recv = 0
        self.fail = 0
        self.trans = 0
        self.d = Deferred()
        self.ping_prog = "/usr/bin/ping"

    def ping(self):
        reactor.spawnProcess(self, self.ping_prog, [self.ping_prog, "-c", count, ipaddr])


    def getDeferred(self):
        return self.d

    def outReceived(self, data):
        self.data += data

    def outConnectionLost(self):
        self.recv = int(self.received_re.search(self.data).group(1))
        self.trans = int(self.transmitted_re.search(self.data).group(1))
        self.fail = self.trans - self.recv
        if self.recv > self.fail:
            self.d.callback(self)
        else:
            self.d.errback()

    def get_recv(self):
        return self.recv

    def get_fail(self):
        return self.fail

if __name__=="__main__":
    from twisted.python import log
    log.startLogging(open('log/pingtest.log', 'w'))
    def check_services(result, pingobj):
        try:
            print "Got %d good pings" % pingobj.get_recv()
            print "Got %d bad pings" % pingobj.get_fail()
        except:
            log.err()
    def ping_fail(failure):
        print "It failed!!"
    import sys
    ping = "/usr/bin/ping"
    ipaddr = sys.argv[1]
    count = str(5)
    pingobj = PingProtocol(ipaddr)
    ping_d = pingobj.getDeferred()
    ping_d.addCallback(check_services, pingobj)
    ping_d.addErrback(ping_fail)
    pingobj.ping()
    #reactor.spawnProcess(pingobj, ping, [ping, "-c", count, ipaddr])
    reactor.callLater(8, reactor.stop)
    reactor.run()
