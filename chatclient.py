#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from twisted.cred import credentials
import gtk
import gtk.glade

from chatserver import ChatProtocol, default_port, Login
import connect

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
        self.username = None
        self.password = None

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
        connect_dialog = connect.ConnectDialog(self.connect_to_server)

    def connect_finished(self, protocol, username, password):
        self.protocol = protocol

    def connect_to_server(self, host, port, username, password):
        if (self.protocol is None or host != self.host or port != self.port or 
          username != self.username or password != self.password):
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            client_creator = ClientCreator(reactor, ChatProtocol, None)
            d1 = client_creator.connectTCP(self.host, self.port)
            d1.addCallback(lambda p: p.callRemote(Login, username=username, 
              password=password))
            d1.addErrback(self.failure)
        else:
            self.connect_finished(self.protocol)

    def failure(self, error):
        messagedialog = gtk.MessageDialog(parent=self.chat_window, 
          type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK,
          message_format="Could not connect to %s:%s\n%s" % (self.host, 
            self.port, error))
        messagedialog.run()
        messagedialog.destroy()

    def stop(self, unused):
        reactor.stop()


if __name__ == '__main__':
    chatclient = ChatClient()
    reactor.run()
