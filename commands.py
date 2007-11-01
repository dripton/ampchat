#!/usr/bin/env python

from twisted.protocols import amp
from twisted.cred.error import UnauthorizedLogin

# commands to server side

class Login(amp.Command):
    arguments = [("username", amp.String()), ("password", amp.String())]
    response = []
    errors = {UnauthorizedLogin: "UnauthorizedLogin"}
    # If we set requiresAnswer = False, then the client-side callRemote
    # returns None instead of a deferred, and we can't attach callbacks.
    # So be sure to return an empty dict instead.
    # TODO doc patch for twisted

class SendToAll(amp.Command):
    arguments = [("message", amp.String())]
    response = []

class SendToUser(amp.Command):
    arguments = [("message", amp.String()), "username", amp.String()]
    response = []


# commands to client side

class Send(amp.Command):
    arguments = [("message", amp.String()), ("sender", amp.String())]
    response = []

class AddUser(amp.Command):
    arguments = [("user", amp.String())]
    response = []

class DelUser(amp.Command):
    arguments = [("user", amp.String())]
    response = []

class LoggedIn(amp.Command):
    arguments = [("ok", amp.Boolean())]
    response = []