#!/usr/bin/env python

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from diceserver import RollDice


def roll_die():
    d1 = ClientCreator(reactor, amp.AMP).connectTCP(
        '127.0.0.1', 1234).addCallback(
            lambda p: p.callRemote(RollDice, sides=6)).addCallback(
                lambda result: result['result'])
    def done(result):
        print 'Got roll:', result
        reactor.stop()
    d1.addCallback(done)

if __name__ == '__main__':
    roll_die()
    reactor.run()
