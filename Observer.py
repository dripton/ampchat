import zope.interface

class IObserver(zope.interface.Interface):

    def update(observed, action):
        """Inform this observer that action has happened to observed.

        observed may be None, in which case action should contain
        all necessary information.
        """
