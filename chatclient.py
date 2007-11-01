#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
from twisted.cred import credentials
from twisted.cred.error import UnauthorizedLogin
import gtk
import gtk.glade

from chatserver import default_port
from connect import ConnectDialog
import commands

default_host = "localhost"



class ChatClientProtocol(amp.AMP):
    def __init__(self, *args):
        print "ChatClientProtocol.__init__", self, args
        super(ChatClientProtocol, self).__init__()
        self.users = set()

    def send(self, message, sender):
        """Send message to this client from sender"""
        #TODO
        return {}
    commands.Send.responder(send)

    def add_user(self, user):
        self.users.add(user)
        return {}
    commands.AddUser.responder(add_user)

    def del_user(self, user):
        self.users.discard(user)
        return {}
    commands.DelUser.responder(add_user)

    def logged_in(self, ok):
        pass
        #TODO
    commands.LoggedIn.responder(logged_in)


class ChatClientFactory(_InstanceFactory):
    protocol = ChatClientProtocol

    def __repr__(self):
        return "<ChatClient factory: %r>" % (self.instance, )


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
        self.vbox1.reorder_child(self.chat_window.ui_manager.get_widget(
          "/Menubar"), 0)

        self.chat_window.set_default_size(200, 100)
        self.chat_window.connect("destroy", self.stop)
        self.chat_window.set_title("AMP Chat Demo")
        self.chat_window.show()

        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.chat_entry.show()

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
        connect_dialog = ConnectDialog(self.connect_to_server)

    def connect_to_server(self, host, port, username, password):
        print("connect_to_server")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        deferred = defer.Deferred()
        self.factory = ChatClientFactory(reactor, ChatClientProtocol(), 
          deferred)
        connector = reactor.connectTCP(self.host, self.port, self.factory)
        deferred.addCallback(self.connected_to_server)
        deferred.addErrback(self.failure)
        return deferred

    def connected_to_server(self, protocol):
        print("connected_to_server", protocol)
        self.protocol = protocol
        deferred = protocol.callRemote(commands.Login, username=self.username, 
          password=self.password)
        deferred.addCallback(self.connect_finished)
        deferred.addErrback(self.failure)

    def connect_finished(self, result):
        print("connect_finished", result)

    def failure(self, error):
        print("failure", error)
        messagedialog = gtk.MessageDialog(parent=self.chat_window, 
          type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK,
          message_format="Could not connect to %s:%s\n%s" % (self.host, 
            self.port, error))
        messagedialog.run()
        messagedialog.destroy()

    def stop(self, unused):
        reactor.stop()

    def cb_keypress(self, entry, event):
        ENTER_KEY = 65293   # XXX Find a cleaner way
        if event.keyval == ENTER_KEY:
            text = self.chat_entry.get_text()
            if text and self.protocol is not None:
                # TODO If a username is highlighted, SendToUser
                deferred = self.protocol.callRemote(commands.SendToAll, 
                  message=text)
                deferred.addErrback(self.failure)
                self.chat_entry.set_text("")


if __name__ == "__main__":
    chatclient = ChatClient()
    reactor.run()
