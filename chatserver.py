#!/usr/bin/env python

import sys

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.python import usage
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal
from twisted.cred import credentials

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

    @commands.Login.responder
    def login(self, username, password):
        """Attempt to login."""
        if username in self.factory.username_to_protocol:
            raise commands.LoginError("User '%s' already logged in" % username)
        creds = credentials.UsernamePassword(username, password)
        deferred = self.factory.portal.login(creds, None, IAvatar)
        deferred.addCallback(self.login_succeeded)
        deferred.addErrback(self.login_failed)
        return deferred

    def login_succeeded(self, (avatar_interface, avatar, logout)):
        name = avatar.name
        self.username = name
        self.factory.username_to_protocol[name] = self
        # Tell all users about this user
        for protocol in self.factory.username_to_protocol.itervalues():
            protocol.callRemote(commands.AddUser, user=name)
        # Tell this user about all other users
        for username in self.factory.username_to_protocol:
            if username != name:
                self.callRemote(commands.AddUser, user=username)
        return {}

    def login_failed(self, failure):
        raise commands.LoginError("Incorrect username or password")

    @commands.SendToUser.responder
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

    @commands.SendToAll.responder
    def send_to_all(self, message):
        for protocol in self.factory.username_to_protocol.itervalues():
            protocol.callRemote(commands.Send, message=message,
              sender=self.username)
        return {}

    def connectionLost(self, unused):
        try:
            del self.factory.username_to_protocol[self.username]
        except KeyError:
            pass
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
