#!/usr/bin/env python

import gtk
import gtk.glade

from chatserver import default_port

"""Dialog for specifying connection parameters"""

class ConnectDialog(object):
    def __init__(self, callback):
        self.glade = gtk.glade.XML("connect.glade")
        self.widget_names = ["connect_dialog", "hostname_entry", "port_entry",
          "username_entry", "password_entry"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.connect_dialog.show()
        self.connect_dialog.connect("response", self.response)
        self.hostname_entry.set_text("localhost")
        self.port_entry.set_text(str(default_port))
        self.callback = callback

    def response(self, dialog, response_id):
        if response_id == gtk.RESPONSE_OK:
            hostname = self.hostname_entry.get_text()
            if not hostname:
                messagedialog = gtk.MessageDialog(parent=self.connect_dialog,
                  type=gtk.MESSAGE_ERROR,
                  buttons=gtk.BUTTONS_OK, 
                  message_format="Need a hostname")
                messagedialog.run()
                messagedialog.destroy()
                return True
            username = self.username_entry.get_text()
            if not username:
                messagedialog = gtk.MessageDialog(parent=self.connect_dialog,
                  type=gtk.MESSAGE_ERROR,
                  buttons=gtk.BUTTONS_OK, 
                  message_format="Need a username")
                messagedialog.run()
                messagedialog.destroy()
                return True
            password = self.password_entry.get_text()
            if not password:
                messagedialog = gtk.MessageDialog(parent=self.connect_dialog,
                  type=gtk.MESSAGE_ERROR,
                  buttons=gtk.BUTTONS_OK, 
                  message_format="Need a password")
                messagedialog.run()
                messagedialog.destroy()
                return True

            port_str = self.port_entry.get_text()
            try:
                port = int(port_str)
            except ValueError:
                messagedialog = gtk.MessageDialog(parent=self.connect_dialog,
                  type=gtk.MESSAGE_ERROR,
                  buttons=gtk.BUTTONS_OK, 
                  message_format="Port must be a number")
                messagedialog.run()
                messagedialog.destroy()
                return True
            else:
                if port < 1 or port > 65535:
                    messagedialog = gtk.MessageDialog(parent=self.connect_dialog,
                      type=gtk.MESSAGE_ERROR,
                      buttons=gtk.BUTTONS_OK,
                      message_format="Port must be in range 1-65535")
                    messagedialog.run()
                    messagedialog.destroy()
                    return True
            self.callback(hostname, port, username, password)
            self.connect_dialog.destroy()
    

if __name__ == "__main__":
    def print_callback(hostname, port, username, password):
        print("hostname: %s port: %s username: %s" % (hostname, port, 
          username))
        gtk.main_quit()
    connect_dialog = ConnectDialog(print_callback)
    gtk.main()
