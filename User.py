from zope.interface import implements, Interface


class IAvatar(Interface):
    pass


class User(object):
    implements(IAvatar)

    def __init__(self, name, server, client):
        self.name = name
        self.server = server
        self.client = client

    def attached(self, mind):
        print("User.attached", self, mind)

    def logout(self):
        print("User.logout", self)
