#!/usr/bin/env python

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from twisted.internet.protocol import _InstanceFactory
from twisted.protocols import amp
import gtk
import gtk.glade

from chatserver import default_port
from connect import ConnectDialog
import commands

default_host = "localhost"


class ChatClientProtocol(amp.AMP):

    @commands.Send.responder
    def send(self, message, sender):
        """Send message to this client from sender"""
        chatclient.receive_chat_message(message, sender)
        return {}

    @commands.AddUser.responder
    def add_user(self, user):
        if not hasattr(self, "users"):
            self.users = set()
        self.users.add(user)
        chatclient.update_user_store(self.users)
        return {}

    @commands.DelUser.responder
    def del_user(self, user):
        self.users.discard(user)
        chatclient.update_user_store(self.users)
        return {}


class ChatClientFactory(_InstanceFactory):
    protocol = ChatClientProtocol

    def __init__(self, reactor, instance, deferred):
        _InstanceFactory.__init__(self, reactor, instance, deferred)

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
        self.chat_window.set_title("AMP Chat -- not logged in")
        self.chat_window.show()

        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.chat_entry.show()

        self.user_store = gtk.ListStore(str)
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.set_select_function(self.cb_user_list_select, data=None,
          full=True)
        column = gtk.TreeViewColumn("User Name", gtk.CellRendererText(),
          text=0)
        self.user_list.append_column(column)
        self.user_list.show()
        self.selected_names = set()


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
        if self.protocol is not None:
            self.protocol.transport.loseConnection()
        factory = ChatClientFactory(reactor, ChatClientProtocol(), deferred)
        connector = reactor.connectTCP(self.host, self.port, factory)
        deferred.addCallback(self.connected_to_server)
        deferred.addErrback(self.failure)
        return deferred

    def connected_to_server(self, protocol):
        self.protocol = protocol
        deferred = protocol.callRemote(commands.Login, username=self.username, 
          password=self.password)
        deferred.addCallback(self.cb_login)
        deferred.addErrback(self.eb_login)

    def cb_login(self, response):
        chatclient.chat_window.set_title("AMP Chat -- logged in as %s" % 
          chatclient.username)

    def eb_login(self, error):
        chatclient.chat_window.set_title("AMP Chat -- not logged in")
        message_dialog = gtk.MessageDialog(parent=chatclient.chat_window,
          type=gtk.MESSAGE_ERROR, 
          buttons=gtk.BUTTONS_CLOSE,
          message_format=error.getErrorMessage())
        message_dialog.run()
        message_dialog.destroy()

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
        if event.keyval == gtk.keysyms.Return:
            text = self.chat_entry.get_text()
            if text and self.protocol is not None:
                if self.selected_names:
                    deferred = self.protocol.callRemote(commands.SendToUsers,
                      message=text, usernames=self.selected_names)
                else:
                    deferred = self.protocol.callRemote(commands.SendToAll, 
                      message=text)
                deferred.addErrback(self.failure)
                self.chat_entry.set_text("")

    def cb_user_list_select(self, selection, model, path, is_selected, unused):
        index = path[0]
        row = self.user_store[index, 0]
        name = row[0]
        if is_selected:
            self.selected_names.remove(name)
        else:
            self.selected_names.add(name)
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
