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
    # XXX Due to metaclass weirdness with amp.AMP, __init__ never gets
    # run.  So we can't access self.factory.
    # def __init__(self):
    #     amp.AMP.__init__(self)
    #     self.users = set()

    def send(self, message, sender):
        """Send message to this client from sender"""
        chatclient.receive_chat_message(message, sender)
        return {}
    commands.Send.responder(send)

    def add_user(self, user):
        if not hasattr(self, "users"):
            self.users = set()
        self.users.add(user)
        chatclient.update_user_store(self.users)
        return {}
    commands.AddUser.responder(add_user)

    def del_user(self, user):
        self.users.discard(user)
        chatclient.update_user_store(self.users)
        return {}
    commands.DelUser.responder(del_user)

    def logged_in(self, ok):
        return {}
    commands.LoggedIn.responder(logged_in)


class ChatClientFactory(_InstanceFactory):
    protocol = ChatClientProtocol

    def __init__(self, reactor, instance, deferred, chat_client):
        _InstanceFactory.__init__(self, reactor, instance, deferred)
        self.chat_client = chat_client

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

        self.user_store = gtk.ListStore(str)
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        selection.set_select_function(self.cb_user_list_select, data=None,
          full=True)
        column = gtk.TreeViewColumn("User Name", gtk.CellRendererText(),
          text=0)
        self.user_list.append_column(column)
        self.user_list.show()
        self.selected_name = None


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
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        deferred = defer.Deferred()
        self.factory = ChatClientFactory(reactor, 
          ChatClientProtocol(), deferred, self)
        connector = reactor.connectTCP(self.host, self.port, self.factory)
        deferred.addCallback(self.connected_to_server)
        deferred.addErrback(self.failure)
        return deferred

    def connected_to_server(self, protocol):
        self.protocol = protocol
        deferred = protocol.callRemote(commands.Login, username=self.username, 
          password=self.password)
        deferred.addErrback(self.failure)

    def failure(self, error):
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
                if self.selected_name is not None:
                    deferred = self.protocol.callRemote(commands.SendToUser,
                      message=text, username=self.selected_name)
                else:
                    deferred = self.protocol.callRemote(commands.SendToAll, 
                      message=text)
                deferred.addErrback(self.failure)
                self.chat_entry.set_text("")

    def cb_user_list_select(self, selection, model, path, is_selected, unused):
        index = path[0]
        row = self.user_store[index, 0]
        name = row[0]
        if self.selected_name == name:
            self.selected_name = None
        else:
            self.selected_name = name
        return True

    def update_user_store(self, usernames):
        sorted_usernames = sorted(usernames)
        length = len(self.user_store)
        for ii, username in enumerate(sorted_usernames):
            if ii < length:
                self.user_store[ii, 0] = (username,)
            else:
                self.user_store.append((username,))
        length = len(sorted_usernames)
        while len(self.user_store) > length:
            del self.user_store[length]


    def receive_chat_message(self, message, sender):
        buf = self.chat_view.get_buffer()
        message = sender + ": " + message.strip() + "\n"
        it = buf.get_end_iter()
        buf.insert(it, message)
        self.chat_view.scroll_to_mark(buf.get_insert(), 0)


if __name__ == "__main__":
    # XXX Protocol can't find its factory to find the ChatClient, so put it 
    # in a global for now.
    chatclient = ChatClient()
    reactor.run()
