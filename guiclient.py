#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
import gtk
import gtk.glade

from diceserver import RollDice


class GUIClient(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", self.stop)
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        self.event_box = gtk.EventBox()
        self.image = gtk.Image()
        self.image.set_from_file("Die1.png")
        self.image.show()
        self.event_box.add(self.image)
        self.vbox.pack_end(self.event_box)
        button = gtk.Button()
        button.set_label("Roll")
        button.connect("button-press-event", self.roll)
        button.show()
        self.vbox.pack_end(button)
        self.show()

    def roll(self, widget, event):
        d1 = ClientCreator(reactor, amp.AMP).connectTCP(
            '127.0.0.1', 1234).addCallback(
                lambda p: p.callRemote(RollDice, sides=6)).addCallback(
                    lambda result: result['result'])
        def done(result):
            print 'Got roll:', result
            self.event_box.remove(self.image)
            filename = "Die%d.png" % result
            self.image = gtk.Image()
            self.image.set_from_file(filename)
            self.event_box.add(self.image)
            self.image.show()
            self.event_box.show()

        d1.addCallback(done)

    def stop(self, unused):
        reactor.stop()
        gtk.main_quit()

if __name__ == '__main__':
    guiclient = GUIClient()
    reactor.run()
