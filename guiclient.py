#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
import gtk
import gtk.glade

from diceserver import RollDice, port


class GUIClient(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_default_size(200, 100)
        self.connect("destroy", self.stop)
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        button = gtk.Button()
        button.set_label("Roll")
        button.connect("button-press-event", self.roll)
        button.show()
        self.vbox.pack_start(button)
        self.image = gtk.Image()
        self.image.set_size_request(60, 60)
        self.image.show()
        self.vbox.pack_start(self.image)
        self.show()
        self.protocol = None

    def done(self, result):
        self.vbox.remove(self.image)
        filename = "Die%d.png" % result
        self.image = gtk.Image()
        self.image.set_from_file(filename)
        self.vbox.pack_start(self.image)
        self.image.show()

    def roll(self, widget, event):
        host = "localhost"
        clientcreator = ClientCreator(reactor, amp.AMP)
        d1 = clientcreator.connectTCP(host, port)
        d1.addCallback(lambda p: p.callRemote(RollDice, sides=6))
        d1.addCallback(lambda result_dict: result_dict['result'])
        d1.addCallback(self.done)

    def stop(self, unused):
        reactor.stop()


if __name__ == '__main__':
    guiclient = GUIClient()
    reactor.run()
