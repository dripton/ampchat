#!/usr/bin/env python

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.python import usage
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal

import Realm

default_port = 65432


class Options(usage.Options):
    optParameters = [
        ["port", "p", default_port, "server port"],
    ]


class Login(amp.Command):
    arguments = [('username', amp.String()), ('password', amp.String())]
    response = [('ok', amp.Boolean())]

class SendToAll(amp.Command):
    arguments = [('message', amp.String())]
    response = []
    requiresAnswer = False

class SendToUser(amp.Command):
    arguments = [('message', amp.String()), 'username', amp.String()]
    response = []
    requiresAnswer = False


class ChatProtocol(amp.AMP):
    def __init__(self, portal):
        amp.AMP.__init__(self)
        self.portal = portal
        self.username_to_peer = {}

    def login(self, username, password):
        """Attempt to login.

        Return True if successful, False if not.
        """
        self.username_to_peer[username] = self.transport.getPeer()
        ok = True
        return {'ok': ok}
    Login.responder(login)


    def send_to_user(self, message, username):
        peer = self.username_to_peer().get(username)
        if peer is not None:
            peer.callRemote("send_message", message)
        return {}
    SendToUser.responder(send_to_user)

    def send_to_all(self, message):
        peer = self.username_to_peer().get(username)
        if peer is not None:
            peer.callRemote("send_message", message)
        return {}
    SendToAll.responder(send_to_all)


class Server(object):
    pass


class ChatFactory(ServerFactory):

    protocol = ChatProtocol

    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        p = self.protocol(self.portal)
        p.factory = self
        return p


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
    realm = Realm.Realm(server)
    checker = FilePasswordDB("passwd.txt")
    portal = Portal(realm, [checker])
    factory = ChatFactory(portal)
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == '__main__':
    main()
