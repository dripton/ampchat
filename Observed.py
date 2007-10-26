from zope.interface import Interface, implements

class IObserved(Interface):
    def add_observer(observer, name=None):
        """Add an observer to this object."""

    def remove_observer(observer):
        """Remove an observer from this object."""

    def notify(action, names=None):
        """Tell observers about this action."""

class Observed(object):
    """Inherit from this mixin and call its __init__ to allow the class
    to be observed."""

    implements(IObserved)

    def __init__(self):
        self.observers = {}

    def add_observer(self, observer, name=""):
        if observer not in self.observers:
            self.observers[observer] = name

    def remove_observer(self, observer):
        if observer in self.observers:
            del self.observers[observer]

    def notify(self, action, names=None):
        for observer, name in self.observers.iteritems():
            if names is None or name in names:
                observer.update(self, action)