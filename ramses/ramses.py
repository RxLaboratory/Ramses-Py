from .logger import log
from .daemon_interface import RamDaemonInterface
from .ramState import RamState
from .ramSettings import RamSettings
from .ramProject import RamProject


class Ramses:
    """The main class. One (and only one) instance globally available, instantiated during init time.

    Static Attributes:
        instance: Ramses
            The unique Ramses instance
    """

    instance = None

    def __init__(self, port=18185, connect=True):
        """
        Args:
            port (int, optional): Defaults to 18185.
            connect (bool, optional): Defaults to True.

        Raises:
            Exception
        """
        if Ramses.instance:
            raise Exception("There cannot be more than one instance of Ramses. Ramses is a Singleton!")

        self._daemon = RamDaemonInterface()
        self._settings = RamSettings()
        self._offline = False  # If True, never try to connect again

        # autoConnect
        if self._settings.autoConnect:
            self.connect()

        Ramses.instance = self

        # if connect:
        #     self.launchClient( True )

    # PROPERTIES

    def currentProject(self):
        """The current project.

        Returns:
            RamProject or None
        """

        # If online, ask the daemon
        if not self._offline and self._daemon.online():
            # Ask (the daemon returns a dict)
            projDict = self._daemon.getCurrentProject()
            # Check if successful
            if RamDaemonInterface.checkReply(projDict):
                content = projDict['content']

                proj = RamProject(content['name'], content['shortname'], content['width'], content['height'],
                                  content['framerate'], content['folder'])
                return proj

        return None

        # TODO if offline

    def currentStep(self):  # A revoir
        """The current project.

       Returns:
          RamStep or None
        """

        # If online, ask the daemon
        if not self._offline and self._daemon.online():
            # Ask (the daemon returns a dict)
            stepDict = self._daemon.getSteps()
            # Check if successful
            if RamDaemonInterface.checkReply(stepDict):
                content = stepDict['content']
                steps = content['steps']

                step = RamStep(steps['name'], steps['shortname'], steps['folder'], steps['type'])
                return step

        return None

        # TODO if offline

    def currentUser(self):
        """The current user.

        Returns:
            RamUser or None
        """

        # If online, ask the daemon
        if not self._offline and self.connect():
            # Ask (the daemon returns a dict)
            userDict = self._daemon.getCurrentUser()

            # Check if successful
            if RamDaemonInterface.checkReply(userDict):
                content = userDict['content']

                # check role
                role = RamUser.STANDARD
                if content['role'] == 'LEAD':
                    role = RamUser.LEAD
                elif content['role'] == 'PROJECT_ADMIN':
                    role = RamUser.PROJECT_ADMIN
                elif content['role'] == 'ADMIN':
                    role = RamUser.ADMIN

                user = RamUser(content['name'], content['shortName'], content['folderPath'], role)
                return user

        return None

        # TODO if offline

    def online(self):
        """True if connected to the Daemon and the Daemon is responding.

        Returns:
            bool
        """
        return not self._offline

        # PUBLIC
    
    def alternativeFolderPaths(self):  # TODO
        """A list of alternative absolute paths to the main Ramses folder.
        Missing files will be looked for in these paths (and copied to the main path if available),
        and they will be used if the main path is not available.

        Returns:
            str list
        """
        pass

    def backupFolderPath(self):  # TODO
        """A copy of the main folder where all files are stored.

        Returns:
            str
        """
        pass

    def folderPath(self):  # TODO
        """The absolute path to main Ramses folder, containing projects by default,
        config files, user folders, admin files…

        Returns:
            str
        """
        pass

    def connect(self):
        """Checks Daemon availability and initiates the connection. Returns success.

        Returns:
            bool
        """

        log("Checking if the Daemon is available")
        # Check if already online
        daemon = self._daemon
        if daemon.online():
            if daemon.getCurrentUser():
                return True
            else:
                daemon.raiseWindow()
                log("Please, login!")
                return False
        else:
            # TODO launch client
            # wait a few secs
            # if not self.connect()
            self._offline = True

    def disconnect(self):  # TODO
        """Gets back to offline mode.

        Returns:
            bool
        """
        pass

    def daemonInterface(self):
        """The Daemon interface.

        Returns:
            RamDaemonInterface
        """
        return self.__daemon

    def project(self, projectShortName):  # TODO
        """Gets a specific project.

        Args:
            projectShortName (str): projectShortName

        Returns:
            RamProject
        """
        for project in self.projects():
            if project.shortName == projectShortName:
                return project
        return self.project()

    def projects(self):  # TODO
        """The list of available projects.

        Returns:
            list of RamProject
        """
        pass

    def state(self, stateShortName="WIP"):
        """Gets a specific state.

        Args:
            stateShortName (str, optional): Defaults to "WIP".

        Returns:
            RamState
        """
        for state in self.states():
            if state.shortName() == stateShortName():
                return state
        return None

    def states(self):
        """The list of available states.

        Returns:
            list of RamState
        """
        newStateList = []

        # If online, ask the daemon
        if not self._offline and self.connect():
            # Ask (the daemon returns a dict)
            replyDict = self._daemon.getStates()

            # Check if successful
            if RamDaemonInterface.checkReply(replyDict):
                contentDict = statesDict['content']
                statesDict = contentDict['states']

                for state in statesDict:
                    newState = RamState(state['name'], state['shortname'], state['completionRatio'], state['color'])
                    newStateList.append(newState)

                return newStateList

        states = [
            RamState("No", "NO", 1.0, [25,25,25]), # Very dark gray
            RamState("To Do", "TODO", 0.0, [85, 170, 255]), # Blue
            RamState("Work in progress", "WIP", 0.5,  [255,255,127]), # Light Yellow
            RamState("OK", "OK", 1.0, [0, 170, 0]), # Green
        ]
        return states

    def showClient(self):  # TODO
        """Raises the Ramses Client window, launches the client if it is not already running.
        """
        pass

    def settings(self):  # TODO
        """

        Args:
            (RamSettings): settings
        """
        return self._settings

    def version(self):  # TODO
        """The current version of this API

        Returns:
            str
        """
        pass
