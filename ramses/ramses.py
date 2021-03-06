# -*- coding: utf-8 -*-

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import os
from subprocess import Popen, PIPE
from time import sleep

from .file_manager import RamFileManager
from .logger import log
from .constants import FolderNames, LogLevel, Log
from .daemon_interface import RamDaemonInterface
from .ram_settings import RamSettings

settings = RamSettings.instance()
daemon = RamDaemonInterface.instance()

class Ramses( object ):
    """The main class. One (and only one) instance globally available, instantiated during init time.

    Static Attributes:
        instance: Ramses
            The unique Ramses instance
    """

    # API Settings
    _version = settings.version
    apiReferenceUrl = settings.apiReferenceUrl
    addonsHelpUrl = settings.addonsHelpUrl
    generalHelpUrl = settings.generalHelpUrl

    _instance = None

    def __init__(self):
        """
        Ramses is a singleton and cannot be initialized with `Ramses()`. Call Ramses.instance() instead.

        Raises:
            RuntimeError
        """
        raise RuntimeError("Ramses can't be initialized with `Ramses()`, it is a singleton. Call Ramses.instance() instead.")

    @classmethod
    def instance( cls ):
        from .ram_state import RamState

        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._offline = True
            cls._folderPath = ""
            cls._states = []
            cls._currentProject = None
            cls.publishScripts = []
            cls.statusScripts = []
            cls.importScripts = []
            cls.replaceScripts = []
            cls.userScripts = {}

            if settings.online:
                log("I'm trying to contact the Ramses Client.", LogLevel.Info)
                cls._instance.connect()

            # Not documented: the states to use offline
            cls.defaultStates = [
                RamState("No", "NO", 0, [25,25,25]), # Very dark gray
                RamState("To Do", "TODO", 0, [85, 170, 255]), # Blue
                RamState("Work in progress", "WIP", 50,  [255,255,127]), # Light Yellow
                RamState("OK", "OK", 100, [0, 170, 0]), # Green
            ]
            cls.defaultState = cls.defaultStates[2]

        return cls._instance

    def currentProject(self):
        from .ram_project import RamProject
        """The current project.

        Returns:
            RamProject or None
        """
        # If online, ask the daemon
        if not self._offline:
            # Ask (the daemon returns a dict)
            reply = daemon.getCurrentProject()
            # Check if successful
            if RamDaemonInterface.checkReply(reply):     
                return RamProject.fromDict( reply['content'] )  

        return self._currentProject

    def setCurrentProject( self, project ):
        """Sets the current project (useful if offline)"""
        if project is None:
            return
            
        self._currentProject = project

        if not self._offline:
            daemon.setCurrentProject( project.shortName() )

    def currentUser(self):
        from .ram_user import RamUser
        """The current user.

        Returns:
            RamUser or None
        """

        # If online, ask the daemon
        if not self._offline:
            # Ask (the daemon returns a dict)
            reply = daemon.getCurrentUser()

            # Check if successful
            if RamDaemonInterface.checkReply(reply):
                return RamUser.fromDict( reply['content'] )

        return None

    def online(self):
        """True if connected to the Daemon and the Daemon is responding.

        Returns:
            bool
        """
        print("Is Ramses online? " + str(not self._offline))
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

    def folderPath(self):
        """The absolute path to the main Ramses folder, containing projects by default,
        config files, user folders, admin files???

        Returns:
            str
        """

        if self._folderPath != "":
            return self._folderPath

        if not self._offline:
            # Ask (the daemon returns a dict)
            replyDict = daemon.getRamsesFolderPath()

            # Check if successful
            if RamDaemonInterface.checkReply(replyDict):
                self._folderPath = replyDict['content']['folder']
                settings.ramsesFolderPath = self._folderPath
                settings.save()

            return self._folderPath

        # if offline, get from settings
        self._folderPath = settings.ramsesFolderPath
        return self._folderPath

    def projectsPath(self):
        """Returns the default path for projects"""

        folderPath = self.folderPath()
        if folderPath == "":
            return ""

        return RamFileManager.buildPath((
            folderPath,
            FolderNames.projects
        ))

    def usersPath(self):
        """Returns the default path for users"""

        folderPath = self.folderPath()
        if folderPath == "":
            return ""

        return RamFileManager.buildPath((
            folderPath,
            FolderNames.users
        ))

    def connect(self):
        """Checks Daemon availability and initiates the connection. Returns success.

        Returns:
            bool
        """

        # Check if already online
        self._offline = False
        if daemon.online():
            user = self.currentUser()
            if user:
                return True
            else:
                daemon.raiseWindow()
                log( Log.NoUser, LogLevel.Info )
        else:
            # Try to open the client
            self.showClient()

        self._offline = True
        return False

    def disconnect(self):
        """Gets back to offline mode.

        Returns:
            bool
        """
        self._offline = True

    def daemonInterface(self):
        """The Daemon interface.

        Returns:
            RamDaemonInterface
        """
        return daemon

    def project(self, projectShortName):
        """Gets a specific project.

        Args:
            projectShortName (str): projectShortName

        Returns:
            RamProject
        """
        for project in self.projects():
            if project.shortName() == projectShortName:
                return project
        return None

    def projects(self):
        """The list of available projects.

        Returns:
            list of RamProject
        """
        from .ram_project import RamProject

        projects = []

        if not self._offline:
            reply = daemon.getProjects()
            if RamDaemonInterface.checkReply(reply):
                for projectDict in reply['content']['projects']:
                    p = RamProject.fromDict( projectDict )
                    if p is not None:
                        projects.append( p )
                if len(projects) > 0:
                    return projects

        projectsPath = self.projectsPath()
        if projectsPath == "":
            return []

        for projectName in os.listdir(projectsPath):
            projectFolder = RamFileManager.buildPath((
                    projectsPath,
                    projectName
                ))
            p = RamProject.fromPath( projectFolder )
            if p is not None:
                projects.append( p )

        return projects

    def state(self, stateShortName="WIP"):
        """Gets a specific state.

        Args:
            stateShortName (str, optional): Defaults to "WIP".

        Returns:
            RamState
        """

        from .ram_state import RamState

        # If online, ask the daemon
        if not self._offline:
            replyDict = daemon.getState( stateShortName )
            # Check if successful
            if RamDaemonInterface.checkReply(replyDict):
                return RamState.fromDict( replyDict['content'] )

        # Else get in the default list
        for state in self.defaultStates:
            if state.shortName() == stateShortName:
                return state
        
        # Not found
        return self.defaultState

    def states(self):
        """The list of available states.

        Returns:
            list of RamState
        """
        from .ram_state import RamState

        if len(self._states) > 0:
            return self._states

        # If online, ask the daemon
        if not self._offline:
            # Ask (the daemon returns a dict)
            replyDict = daemon.getStates()

            # Check if successful
            if RamDaemonInterface.checkReply(replyDict):
                contentDict = replyDict['content']
                statesDict = contentDict['states']

                for state in statesDict:
                    newState = RamState.fromDict( state )
                    self._states.append(newState)

                return self._states

        return self.defaultStates

    def showClient(self):
        """Raises the Ramses Client window, launches the client if it is not already running.
        """

        if settings.ramsesClientPath == "":
            self._offline = True
            return False

        try:
            p = Popen(settings.ramsesClientPath, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except:
            log("The Client is not available at " + settings.ramsesClientPath, LogLevel.Critical)
            return False

        if not p.poll(): del p
        else:
            log("The Client can't be launched correctly.", LogLevel.Critical)
            return False
        
        # Wait for the client to respond
        numTries = 0
        self._offline = True
        while( self._offline and numTries < 3 ):
            self._offline = not daemon.online()
            sleep(1)
            numTries = numTries + 1
        
        # If the client opened
        if not self._offline:
            daemon.raiseWindow()
            return True
        
        return False
            
    def settings(self):
        """

        Args:
            (RamSettings): settings
        """
        return settings

    @staticmethod
    def version():
        """The current version of this API

        Returns:
            str
        """
        return Ramses._version

    def publish(self, item, step, filePath, publishOptions=None, showPublishOptions=False ):
        """Publishes the item; runs the list of scripts Ramses.publishScripts"""
        for script in self.publishScripts:
            script(item, step, filePath, publishOptions, showPublishOptions)

    def updateStatus(self, item, status, step=None):
        for script in self.statusScripts:
            script( item, status, step)

    def importItem(self, item, filePath, step=None, importOptions=None, showImportOptions=False ):
        for script in self.importScripts:
            script( item, filePath, step, importOptions, showImportOptions )

    def replaceItem(self, item, filePath, step=None, importOptions=None, showImportOptions=False):
        for script in self.replaceScripts:
            script( item, filePath, step, importOptions, showImportOptions )