from twisted.cred.portal import IRealm
from zope.interface import implements

import User

class Realm(object):
    implements(IRealm)

    def __init__(self, server):
        self.server = server

    def requestAvatar(self, avatar_id, mind, *interfaces):
        avatar = User.User(avatar_id, self.server, mind)
        avatar.attached(mind)
