import re
from subprocess import Popen, PIPE
from time import sleep
from sys import platform

from .logger import log
from .daemon_interface import RamDaemonInterface
from .ramState import RamState
from .ramSettings import RamSettings
from .ramUser import RamUser, UserRole

class Ramses:
    """The main class. One (and only one) instance globally available, instantiated during init time.

    Static Attributes:
        instance: Ramses
            The unique Ramses instance
    """
    # The prefixes used in version files which are not states
    _versionPrefixes = ['v','pub']

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
            log("I'm trying to contact the Ramses Client (auto-connection is enabled).")
            self.connect()

        Ramses.instance = self

    def currentProject(self):
        from .ramProject import RamProject
        """The current project.

        Returns:
            RamProject or None
        """

        # If online, ask the daemon
        if not self._offline and self.connect():
            # Ask (the daemon returns a dict)
            projDict = self._daemon.getCurrentProject()
            # Check if successful
            if RamDaemonInterface.checkReply(projDict):
                content = projDict['content']

                proj = RamProject(content['name'], content['shortName'], content['folder'], content['width'],
                                  content['height'], content['framerate'])
                return proj

        return None

        # TODO if offline

    def currentStep(self):  # A revoir
        from .ramStep import RamStep
        """The current project.

        Returns:
          RamStep or None
        """

        # If online, ask the daemon
        if not self._offline and self.connect():
            # Ask (the daemon returns a dict)
            stepDict = self._daemon.getSteps()
            # Check if successful
            if RamDaemonInterface.checkReply(stepDict):
                content = stepDict['content']
                steps = content['steps']

                step = RamStep(steps['name'], steps['shortName'], steps['folder'], steps['type'])
                return step

        return None

        # TODO if offline

    def currentUser(self):
        from .ramUser import RamUser
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
                role = UserRole.STANDARD
                if content['role'] == 'LEAD':
                    role = UserRole.LEAD
                elif content['role'] == 'PROJECT_ADMIN':
                    role = UserRole.PROJECT_ADMIN
                elif content['role'] == 'ADMIN':
                    role = UserRole.ADMIN

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

    def connect(self, overrideAutoConnect=False):
        """Checks Daemon availability and initiates the connection. Returns success.

        Returns:
            bool
        """

        if not self._settings.autoConnect and not overrideAutoConnect:
            return False

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
            # Try to open the client
            self.showClient()

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
        return self._daemon

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
        return None

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
                contentDict = replyDict['content']
                statesDict = contentDict['states']

                for state in statesDict:
                    newState = RamState(state['name'], state['shortName'], state['completionRatio'], state['color'])
                    newStateList.append(newState)

                return newStateList

        return self._settings.defaultStates

    def showClient(self):  # TODO
        """Raises the Ramses Client window, launches the client if it is not already running.
        """

        if self._settings.ramsesClientPath == "":
            self._offline = True
            return False

        try:
            p = Popen(self._settings.ramsesClientPath, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except:
            log("The Client is not available at " + self._settings.ramsesClientPath)
            return False

        if not p.poll(): del p
        else:
            log("The Client can't be launched correctly.")
            return False
        
        # Wait for the client to respond
        numTries = 0
        self._offline = True
        while( self._offline and numTries < 3 ):
            self._offline = not self._daemon.online()
            sleep(1)
            numTries = numTries + 1
        
        # If the client opened
        if not self._offline:
            self._daemon.raiseWindow()
            return True
        
        return False
            
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

    def _decomposeRamsesFileName( self, ramsesFileName ):
        """Low-level, undocumented. Used on files that respect Ramses' naming convention: it separates the name into blocks (one block for the project's shortname, one for the step, one for the extension...)

        A Ramses filename can have all of these blocks:
            projectID_ramType_objectShortName_ramStep_resourceStr_versionBlock.extension
        - ramType can be one of the following letters: A (asset), S (shot), G (general).
        - there is an objectShortName only for assets and shots.
        - resourceStr is optional. It only serves to differentiate the main working file and its resources, that serve as secondary working files.
        - versionBlock is optional. It's made of two blocks: an optional version prefix, also named state, followed by a version number.
            Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ). Eg. 'wip', 'v', ...
        For more information on Ramses' naming conventions (such as length limitation, forbidden characters...), refer to the documentation.

        Arg:
            ramsesFileName: str
        
        Returns: dict or None
            If the file does not match Ramses' naming convention, returns None.
            Else, returns a dictionary made of all the blocks: {"projectId", "ramType", "objectShortName", "ramStep", "resourceStr", "state", "version", "extension"}
        """
        if type(ramsesFileName) != str:
            print("The given filename is not a str.")
            return None

        splitRamsesName = re.match(self._getRamsesNameRegEx(), ramsesFileName)

        if splitRamsesName == None:
            return None

        ramType = ''
        objectShortName = ''

        if splitRamsesName.group(2) in ('A', 'S'):
            ramType = splitRamsesName.group(2)
            objectShortName = splitRamsesName.group(3)
        else:
            ramType = splitRamsesName.group(4)

        optionalBlocks = ['', '', '', '']
        for i in range(0, 4):
            if splitRamsesName.group(i + 6) != None:
                optionalBlocks[i] = splitRamsesName.group( i + 6)

        blocks = {
            "projectID": splitRamsesName.group(1),
            "ramType": ramType,
            "objectShortName": objectShortName,
            "ramStep": splitRamsesName.group(5),
            "resourceStr": optionalBlocks[0],
            "state": optionalBlocks[1],
            "version": optionalBlocks[2],
            "extension": optionalBlocks[3],
        }

        return blocks

    def _isRamsesItemFoldername(self, n):
        """Low-level, undocumented. Used to check if a given folder respects Ramses' naming convention for items' root folders.
        
        The root folder should look like this:
            projectID_ramType_objectShortName

        Returns: bool
        """
        if re.match('^([a-z0-9+-]{1,10})_[ASG]_([a-z0-9+-]{1,10})$' , n , re.IGNORECASE): return True
        return False

    def _getRamsesNameRegEx(self):
        """Low-level, undocumented. Used to get a Regex to check if a file matches Ramses' naming convention.
        """
        regexStr = self._getVersionRegExStr()

        regexStr = '^([a-z0-9+-]{1,10})_(?:([AS])_([a-z0-9+-]{1,10})|(G))_([a-z0-9+-]{1,10})(?:_((?!(?:' + regexStr + ')?[0-9]+)[a-z0-9+\\s-]+))?(?:_(' + regexStr + ')?([0-9]+))?\\.([a-z0-9.]+)$'

        regex = re.compile(regexStr, re.IGNORECASE)
        return regex

    def _getVersionRegExStr(self):
        """Low-level, undocumented. Used to get a Regex str that can be used to identify version blocks.

        A version block is composed of an optional version prefix and a version number.
        'wip002', 'v10', '1002' are version blocks; '002wip', '10v', 'v-10' are not.\n
        Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ).
        """
        
        prefixes = self._versionPrefixes

        for state in self.states():
            prefixes.append( state.shortName() )

        regexStr = ''
        for prefix in prefixes[0:-1]:
            regexStr = regexStr + prefix + '|'
        regexStr = regexStr + prefixes[-1]
        return regexStr
