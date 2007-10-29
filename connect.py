#!/usr/bin/env python

import gtk
import gtk.glade

"""Dialog for specifying connection parameters"""

class ConnectDialog(object):
    def __init__(self, callback):
        self.glade = gtk.glade.XML("connect.glade")
        self.widget_names = ["connect_dialog", "hostname_entry", "port_entry"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.connect_dialog.show()
        self.connect_dialog.connect("response", self.response)
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
        self.callback(hostname, port)
        self.connect_dialog.destroy()
    

if __name__ == "__main__":
    def print_callback(hostname, port):
        print("hostname: %s port: %s" % (hostname, port))
        gtk.main_quit()
    connect_dialog = ConnectDialog(print_callback)
    gtk.main()
