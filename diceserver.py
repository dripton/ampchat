#!/usr/bin/env python

import random

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.python import usage

default_port = 1234

_rand = random.Random()

class Options(usage.Options):
    optParameters = [
        ["port", "p", default_port, "server port"],
    ]

class RollDice(amp.Command):
    arguments = [('sides', amp.Integer())]
    response = [('result', amp.Integer())]


class Dice(amp.AMP):
    def roll(self, sides=6):
        """Return a random integer from 1 to sides"""
        result = _rand.randint(1, sides)
        return {'result': result}
    RollDice.responder(roll)


def main():
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, err:
        print "%s: %s" % (sys.argv[0], err)
        print "%s: Try --help for usage details" % sys.argv[0]
        sys.exit(1)
    port = int(options["port"])

    pf = Factory()
    pf.protocol = Dice
    reactor.listenTCP(port, pf)
    reactor.run()

if __name__ == '__main__':
    main()
