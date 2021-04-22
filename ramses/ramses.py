from .daemon_interface import RamDaemonInterface
from .ramState import RamState


class Ramses:
    """The main class. One (and only one) instance globally available, instantiated during init time.

    Static Attributes:
        instance: Ramses
            The unique Ramses instance
    """

    instance = None

    def __init__( self, port = 18185, connect = True ):
        """
        Args:
            port (int, optional): Defaults to 18185.
            connect (bool, optional): Defaults to True.

        Raises:
            Exception
        """
        if Ramses.instance:
            raise Exception( "There cannot be more than one instance of Ramses. Ramses is a Singleton!" )

        self.__daemon = RamDaemonInterface()
        self.port = port
        self._currentProject = None
        self._currentStep = None
        self._currentUser = None
        self._online = False

        Ramses.instance = self

        # if connect:
        #     self.launchClient( True )

    # PROPERTIES

    @property
    def currentProject( self ):
        """The current project.

        Returns:
            RamProject or None
        """
        return self._currentProject

    @property
    def currentStep( self ):
        """The current project.

        Returns:
            RamStep or None
        """
        return self._currentStep

    @property
    def currentUser( self ):
        """The current user.

        Returns:
            RamUser or None
        """
        return self._currentUser

    @property
    def online( self ):
        """True if connected to the Daemon and the Daemon is responding.

        Returns:
            bool
        """
        return self._online

    # PUBLIC

    def alternativeFolderPaths( self ): #TODO
        """A list of alternative absolute paths to the main Ramses folder.
        Missing files will be looked for in these paths (and copied to the main path if available),
        and they will be used if the main path is not available.

        Returns:
            str list
        """
        pass
        
    def backupFolderPath( self ): #TODO
        """A copy of the main folder where all files are stored.

        Returns:
            str
        """
        pass 

    def folderPath( self ): #TODO
        """The absolute path to main Ramses folder, containing projects by default,
        config files, user folders, admin files…

        Returns:
            str
        """
        pass

    def connect( self ): #TODO
        """Checks Daemon availability and initiates the connection. Returns success.

        Returns:
            bool 
        """
        pass

    def disconnect( self ): #TODO
        """Gets back to offline mode.

        Returns:
            bool
        """
        pass

    def daemonInterface ( self ):
        """The Daemon interface.

        Returns:
            RamDaemonInterface
        """
        return self.__daemon

    def project( self, projectShortName ): #TODO
        """Gets a specific project.

        Args:
            projectShortName (str): projectShortName        

        Returns:
            RamProject
        """
        pass

    def projects( self ): #TODO
        """The list of available projects.

        Returns:
            list of RamProject
        """
        pass

    def state( self, stateShortName="WIP" ):
        """Gets a specific state.

        Args:
            stateShortName (str, optional): Defaults to "WIP".

        Returns:
            RamState
        """
        for state in self.states():
            if state.shortName == stateShortName:
                return state
        return self.state() 

    def states( self ): #TODO get the list from the client
        """The list of available states.

        Returns:
            list of RamSate
        """
        states = [
            RamState("No", "NO", 1.0),
            RamState("To Do", "TODO", 0.0),
            RamState("Work in progress", "WIP", 0.2),
            RamState("OK", "OK", 1.0),
        ]
        return states

    def showClient( self ): #TODO
        """Raises the Ramses Client window, launches the client if it is not already running.
        """
        pass

    def settings( self, autoConnect=True, ramsesClientPath="", ramsesClientPort=18185, folderPath="",  filePath="" ): #TODO
        """

        Args:
            (RamSettings): settings
        """
        pass

    def version( self ): #TODO
        """The current version of this API

        Returns:
            str
        """
        pass
