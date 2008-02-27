from twisted.protocols import amp

# Exceptions
class LoginError(Exception):
    pass
# commands to server side


class Login(amp.Command):
    arguments = [("username", amp.String()), ("password", amp.String())]
    response = []
    errors = {LoginError: "LoginError"}

class SendToAll(amp.Command):
    arguments = [("message", amp.String())]
    response = []

class SendToUser(amp.Command):
    arguments = [("message", amp.String()), ("username", amp.String())]
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


