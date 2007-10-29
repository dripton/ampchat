#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
import gtk
import gtk.glade

from chatserver import ChatProtocol, default_port

default_host = "localhost"

ui_string = """<ui>
  <menubar name="Menubar">
    <menu action="FileMenu">
      <menuitem action="Connect"/>
      <menuitem action="Quit"/>
    </menu>
  </menubar>
</ui>"""

class ChatClient(object):
    def __init__(self):
        self.protocol = None
        self.host = None
        self.port = None

        self.glade = gtk.glade.XML("chat.glade")
        self.widget_names = ["chat_window", "chat_view", "chat_entry", 
          "user_list", "vbox1"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.create_ui()
        self.vbox1.pack_start(self.chat_window.ui_manager.get_widget(
          "/Menubar"), False, False, 0)

        self.chat_window.set_default_size(200, 100)
        self.chat_window.connect("destroy", self.stop)
        self.chat_window.set_title("AMP Chat Demo")
        self.chat_window.show()

    def create_ui(self):
        action_group = gtk.ActionGroup("MasterActions")
        actions = [
          ("FileMenu", None, "_File"),
          ("Connect", None, "_Connect", None, "Connect", 
            self.create_connect_dialog),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program", 
            self.stop),
        ]
        action_group.add_actions(actions)
        self.chat_window.ui_manager = gtk.UIManager()
        self.chat_window.ui_manager.insert_action_group(action_group, 0)
        self.chat_window.ui_manager.add_ui_from_string(ui_string)
        self.chat_window.add_accel_group(
          self.chat_window.ui_manager.get_accel_group())

    def create_connect_dialog(self, action):
        print "create_connect_dialog", self, action

    def done(self, result):
        print "done"

    def connect_finished(self, protocol):
        self.protocol = protocol
        d1 = protocol.callRemote(RollDice, sides=6)
        d1.addCallback(lambda result_dict: result_dict['result'])
        d1.addCallback(self.done)

    def connect_to_server(self, widget):
        host = self.hostname_entry.get_text()
        port_str = self.port_entry.get_text()
        try:
            port = int(port_str)
        except ValueError:
            messagedialog = gtk.MessageDialog(self, type=gtk.MESSAGE_ERROR, 
              buttons=gtk.BUTTONS_OK, message_format="Port must be a number")
            messagedialog.run()
            messagedialog.destroy()
            self.port = None
            return
        else:
            if port < 1 or port > 65535:
                messagedialog = gtk.MessageDialog(self, type=gtk.MESSAGE_ERROR,
                  buttons=gtk.BUTTONS_OK, 
                  message_format="Port must be in range 1-65535")
                messagedialog.run()
                messagedialog.destroy()
                self.port = None
                return
        if self.protocol is None or host != self.host or port != self.port:
            self.host = host
            self.port = port
            clientcreator = ClientCreator(reactor, amp.AMP)
            d1 = clientcreator.connectTCP(self.host, self.port)
            d1.addCallback(self.connect_finished)
            d1.addErrback(self.failure)
        else:
            self.connect_finished(self.protocol)

    def failure(self, error):
        messagedialog = gtk.MessageDialog(self, type=gtk.MESSAGE_ERROR, 
          buttons=gtk.BUTTONS_OK, 
          message_format="Could not connect to %s:%s" % (self.host, self.port))
        messagedialog.run()
        messagedialog.destroy()

    def stop(self, unused):
        reactor.stop()


if __name__ == '__main__':
    chatclient = ChatClient()
    reactor.run()
