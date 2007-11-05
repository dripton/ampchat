#!/usr/bin/env python

import sys

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.python import usage
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal
from twisted.cred import credentials
from twisted.cred.error import UnauthorizedLogin

from Realm import Realm, IAvatar
import commands

default_port = 65432


class Options(usage.Options):
    optParameters = [
        ["port", "p", default_port, "server port"],
    ]



class ChatProtocol(amp.AMP):
    # XXX Not actually called
    def __init__(self):
        amp.AMP.__init__(self)
        self.username = None

    def login(self, username, password):
        """Attempt to login."""
        creds = credentials.UsernamePassword(username, password)
        deferred = self.factory.portal.login(creds, None, IAvatar)
        deferred.addCallback(self.login_succeeded)
        deferred.addErrback(self.login_failed)
        # We need to wait for the deferred to fire, so we can't return an
        # answer yet.
        return {} 
    commands.Login.responder(login)

    def login_succeeded(self, (avatar_interface, avatar, logout)):
        name = avatar.name
        self.username = name
        self.factory.username_to_protocol[name] = self
        self.callRemote(commands.LoggedIn, ok=True)
        # Tell all users about this user
        for protocol in self.factory.username_to_protocol.itervalues():
            protocol.callRemote(commands.AddUser, user=name)
        # Tell this user about all other users
        for username in self.factory.username_to_protocol.iterkeys():
            if username != name:
                self.callRemote(commands.AddUser, user=username)

    def login_failed(self, failure):
        self.callRemote(commands.LoggedIn, ok=False)

    def send_to_user(self, message, username):
        protocol = self.factory.username_to_protocol.get(username)
        if protocol:
            protocol.callRemote(commands.Send, message=message, 
              sender=self.username)
            # Also show it to the sender
            if username != self.username:
                self.callRemote(commands.Send, message=message,
                  sender=self.username)
        return {}
    commands.SendToUser.responder(send_to_user)

    def send_to_all(self, message):
        for protocol in self.factory.username_to_protocol.itervalues():
            protocol.callRemote(commands.Send, message=message,
              sender=self.username)
        return {}
    commands.SendToAll.responder(send_to_all)

    def connectionLost(self, unused):
        del self.factory.username_to_protocol[self.username]
        for protocol in self.factory.username_to_protocol.itervalues():
            protocol.callRemote(commands.DelUser, user=self.username)


class ChatFactory(ServerFactory):
    protocol = ChatProtocol

    def __init__(self, portal):
        self.portal = portal
        self.username_to_protocol = {}


def main():
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, err:
        print "%s: %s" % (sys.argv[0], err)
        print "%s: Try --help for usage details" % sys.argv[0]
        sys.exit(1)
    port = int(options["port"])

    realm = Realm()
    checker = FilePasswordDB("passwd.txt")
    portal = Portal(realm, [checker])
    factory = ChatFactory(portal)
    reactor.listenTCP(port, factory)
    reactor.run()


if __name__ == "__main__":
    main()
