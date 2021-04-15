from .daemon_interface import RamDaemonInterface

class Ramses():
    """The main class. One (and only one) instance globally available, instantiated during init time.

    Static Attributes:
        instance: Ramses
            The unique Ramses instance
    """

    instance = None

    def __init__(self, port = 1818, connect = True):
        if Ramses.instance:
            raise Exception("There cannot be more than one instance of Ramses")

        self.daemon = RamDaemonInterface()

        Ramses.instance = self

    # PUBLIC

    def daemonInterface(self):
        return self.daemon