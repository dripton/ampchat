from twisted.cred.portal import IRealm
from zope.interface import implements, Interface


class IAvatar(Interface):
    pass

class Avatar(object):
    implements(IAvatar)

    def __init__(self, name):
        self.name = name

    def logout(self):
        return

class Realm(object):
    implements(IRealm)

    def requestAvatar(self, avatar_id, mind, *interfaces):
        if IAvatar in  interfaces:
            avatar = Avatar(avatar_id)
            return (IAvatar, avatar, avatar.logout)
        else:
            raise KeyError("Requested interfaces not supported")
