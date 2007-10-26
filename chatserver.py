#!/usr/bin/env python

from twisted.protocols import amp
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.python import usage
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal

import Realm

default_port = 65432


class Options(usage.Options):
    optParameters = [
        ["port", "p", default_port, "server port"],
    ]

class LogIn(amp.Command):
    arguments = [('username', amp.String()), ('password', amp.String())]
    response = [('ok', amp.Boolean())]

class SendToAll(amp.Command):
    arguments = [('message', amp.String())]
    response = [('ok', amp.Boolean())]

class SendToUser(amp.Command):
    arguments = [('message', amp.String()), 'username', amp.String()]
    response = [('ok', amp.Boolean())]


class ChatProtocol(amp.AMP):
    def __init__(self):
        amp.AMP.__init__(self)
        self.username_to_peer = {}

    def login(self, username, password):
        """Attempt to login.
        
        Return True if successful, False if not.
        """
        # For now we allow anyone to login.
        self.username_to_peer[username] = self.transport.getPeer()
        ok = True
        return {'ok': ok}
    LogIn.responder(login)

    def send_to_user(self, message, username):
        peer = self.username_to_peer().get(username)
        if peer is not None:
            peer.callRemote("send_message", message)
            ok = True
        else:
            ok = False
        return {'ok': ok}

class Server(object):
    pass

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
    factory = Factory(portal)
    factory.protocol = ChatProtocol
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == '__main__':
    main()
