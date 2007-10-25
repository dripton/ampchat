#!/usr/bin/env python

import sys

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from twisted.python import usage

from diceserver import RollDice, port


class Options(usage.Options):
        optParameters = [
            ["host", "h", "localhost", "server hostname"],
            ["port", "p", port, "server port"],
        ]


def roll_die(host, port):
    clientcreator = ClientCreator(reactor, amp.AMP)
    d1 = clientcreator.connectTCP(host, port)
    d1.addCallback(lambda p: p.callRemote(RollDice, sides=6))
    d1.addCallback(lambda result: result['result'])
    def done(result):
        print 'Got roll:', result
        reactor.stop()
    d1.addCallback(done)
    d1.addErrback(failure)

def failure(error):
    print "failed", str(error)
    reactor.stop()

if __name__ == '__main__':
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, err:
        print "%s: %s" % (sys.argv[0], err)
        print "%s: Try --help for usage details" % sys.argv[0]
        sys.exit(1)

    host = options["host"]
    port = int(options["port"])
    roll_die(host, port)
    reactor.run()
