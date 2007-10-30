#!/usr/bin/env python

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.python import usage
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal
from twisted.cred import credentials
from twisted.cred.error import UnauthorizedLogin

from Realm import Realm
from User import IAvatar

default_port = 65432


class Options(usage.Options):
    optParameters = [
        ["port", "p", default_port, "server port"],
    ]


# commands in ChatProtocol

class Login(amp.Command):
    arguments = [("username", amp.String()), ("password", amp.String())]
    response = []
    errors = {UnauthorizedLogin: "UnauthorizedLogin"}
    # If we set requiresAnswer = False, then the client-side callRemote
    # returns None instead of a deferred, and we can't attach callbacks.
    # So be sure to return an empty dict instead.

class SendToAll(amp.Command):
    arguments = [("message", amp.String())]
    response = []
    requiresAnswer = False

class SendToUser(amp.Command):
    arguments = [("message", amp.String()), "username", amp.String()]
    response = []
    requiresAnswer = False


class ChatProtocol(amp.AMP):
    # XXX Why are we getting a variable number of args here?
    def __init__(self, *args):
        print "ChatProtocol.__init__", self, args
        super(ChatProtocol, self).__init__()

    def login(self, username, password):
        """Attempt to login."""
        creds = credentials.UsernamePassword(username, password)
        deferred = self.factory.portal.login(creds, None, IAvatar)
        deferred.addCallback(self.login_succeeded)
        deferred.addErrback(self.login_failed)
        return {}
    Login.responder(login)

    def login_succeeded(self):
        print "login_succeeded"

    def login_failed(self):
        print "login_failed"

    def send_to_user(self, message, username):
        peer.callRemote("send_message", message)
        return {}
    SendToUser.responder(send_to_user)

    def send_to_all(self, message):
        peer.callRemote("send_message", message)
        return {}
    SendToAll.responder(send_to_all)


# commands in ChatClientProtocol

class Send(amp.Command):
    arguments = [("message", amp.String()), ("sender", amp.String())]
    response = []
    requiresAnswer = False

class AddUser(amp.Command):
    arguments = [("user", amp.String())]
    response = []
    requiresAnswer = False

class DelUser(amp.Command):
    arguments = [("user", amp.String())]
    response = []
    requiresAnswer = False


class ChatClientProtocol(amp.AMP):
    def __init__(self, *args):
        print "ChatClientProtocol.__init__", self, args
        super(ChatClientProtocol, self).__init__()
        self.users = set()

    def send(self, message, sender):
        """Send message to this client from sender"""
        #TODO
        return {}
    Send.responder(send)

    def add_user(self, user):
        self.users.add(user)
        return {}
    AddUser.responder(add_user)

    def del_user(self, user):
        self.users.discard(user)
        return {}
    DelUser.responder(add_user)

class Server(object):
    pass


class ChatFactory(ServerFactory):
    protocol = ChatProtocol

    def __init__(self, portal):
        self.portal = portal

class ChatClientFactory(ClientFactory):
    protocol = ChatClientProtocol


def main():
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, err:
        print "%s: %s" % (sys.argv[0], err)
        print "%s: Try --help for usage details" % sys.argv[0]
        sys.exit(1)
    port = int(options["port"])

    server = Server()
    realm = Realm(server)
    checker = FilePasswordDB("passwd.txt")
    portal = Portal(realm, [checker])
    factory = ChatFactory(portal)
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == "__main__":
    main()
