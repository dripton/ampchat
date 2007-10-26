#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
import gtk

from diceserver import RollDice, default_port

default_host = "localhost"

class GUIClient(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_default_size(200, 100)
        self.connect("destroy", self.stop)
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()

        hbox1 = gtk.HBox()
        hbox1.show()
        self.vbox.pack_start(hbox1)
        server_label = gtk.Label("Server")
        server_label.show()
        hbox1.pack_start(server_label)
        self.hostname_entry = gtk.Entry()
        self.hostname_entry.set_text(default_host)
        self.hostname_entry.show()
        hbox1.pack_start(self.hostname_entry)

        hbox2 = gtk.HBox()
        hbox2.show()
        self.vbox.pack_start(hbox2)
        port_label = gtk.Label("Port")
        port_label.show()
        hbox2.pack_start(port_label)
        self.port_entry = gtk.Entry()
        self.port_entry.set_text(str(default_port))
        self.port_entry.show()
        hbox2.pack_start(self.port_entry)

        button = gtk.Button()
        button.set_label("Roll")
        button.connect("clicked", self.roll)
        button.show()
        self.vbox.pack_start(button)

        self.image = gtk.Image()
        self.image.set_size_request(60, 60)
        self.image.show()
        self.vbox.pack_start(self.image)

        self.show()

        self.protocol = None
        self.host = None
        self.port = None

    def done(self, result):
        self.vbox.remove(self.image)
        filename = "Die%d.png" % result
        self.image = gtk.Image()
        self.image.set_from_file(filename)
        self.vbox.pack_start(self.image)
        self.image.show()

    def connect_finished(self, protocol):
        self.protocol = protocol
        d1 = protocol.callRemote(RollDice, sides=6)
        d1.addCallback(lambda result_dict: result_dict['result'])
        d1.addCallback(self.done)

    def roll(self, widget):
        host = self.hostname_entry.get_text()
        port_str = self.port_entry.get_text()
        try:
            port = int(port_str)
        except ValueError:
            self.port = None
            self.port_entry.set_text("")
            return
        if self.protocol is None or host != self.host or port != self.port:
            self.host = host
            self.port = port
            clientcreator = ClientCreator(reactor, amp.AMP)
            d1 = clientcreator.connectTCP(self.host, self.port)
            d1.addCallback(self.connect_finished)
        else:
            self.connect_finished(self.protocol)

    def stop(self, unused):
        reactor.stop()


if __name__ == '__main__':
    guiclient = GUIClient()
    reactor.run()
