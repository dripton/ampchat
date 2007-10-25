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

    def roll(self, widget, event):
        host = "127.0.0.1"
        d1 = ClientCreator(reactor, amp.AMP).connectTCP(
            host, port).addCallback(
                lambda p: p.callRemote(RollDice, sides=6)).addCallback(
                    lambda result: result['result'])
        def done(result):
            self.vbox.remove(self.image)
            filename = "Die%d.png" % result
            self.image = gtk.Image()
            self.image.set_from_file(filename)
            self.vbox.pack_start(self.image)
            self.image.show()

        d1.addCallback(done)

    def stop(self, unused):
        reactor.stop()
        gtk.main_quit()

if __name__ == '__main__':
    guiclient = GUIClient()
    reactor.run()
