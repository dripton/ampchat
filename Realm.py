from twisted.cred.portal import IRealm
from zope.interface import implements, Interface

from User import IAvatar, User


class Realm(object):
    implements(IRealm)

    def __init__(self, server):
        self.server = server

    def requestAvatar(self, avatar_id, mind, *interfaces):
        print "Realm.requestAvatar", avatar_id, mind, interfaces
        if IAvatar in interfaces:
            avatar = User(avatar_id, self.server, mind)
            avatar.attached(mind)
            return IAvatar, avatar, avatar.logout
        else:
            raise KeyError("Requested interfaces not supported")
