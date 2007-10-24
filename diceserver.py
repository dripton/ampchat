#!/usr/bin/env python

import random

from twisted.protocols import amp

_rand = random.Random()

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
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory
    pf = Factory()
    pf.protocol = Dice
    reactor.listenTCP(1234, pf)
    reactor.run()

if __name__ == '__main__':
    main()
