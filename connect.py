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
            port = self.port_entry.get_text()
            self.callback(hostname, port)
    

if __name__ == "__main__":
    def print_callback(hostname, port):
        print("hostname: %s port: %s" % (hostname, port))
    connect_dialog = ConnectDialog(print_callback)
    response = connect_dialog.connect_dialog.run()
