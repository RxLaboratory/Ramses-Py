import os
import platform
import json
from .ramState import RamState
from .logger import (
    log,
    LogLevel
)

class ItemType():
    GENERAL='G'
    ASSET='A'
    SHOT='S'

class FolderNames():
    preview = "_preview"
    versions = "_versions"
    publish = "_published"
    userConfig = "Config"
    stepTemplates = "Templates"

# API Settings
version = "0.0.1-dev"
apiReferenceUrl = "https://ramses-docs.rainboxlab.org/dev/add-ons-reference/"
addonsHelpUrl = "https://ramses-docs.rainboxlab.org/addons/"
generalHelpUrl = "https://ramses-docs.rainboxlab.org/"
# Default values
defaultOnline = True # Wether to always try to (re)connect to the Daemon if offline.
defaultRamsesClientPath = "" # Location of the Ramses Client executable file (.exe on Windows, .app on MacOS, .appimage or binary on Linux)
defaultRamsesClientPort = 18185 # Listening port of the Ramses Daemon
defaultLogLevel = LogLevel.Info
# Not Documented: these are not settings to be customized (yet)
folderNames = FolderNames()
defaultStates = [
    RamState("No", "NO", 0, [25,25,25]), # Very dark gray
    RamState("To Do", "TODO", 0, [85, 170, 255]), # Blue
    RamState("Work in progress", "WIP", 50,  [255,255,127]), # Light Yellow
    RamState("OK", "OK", 100, [0, 170, 0]), # Green
]
versionPrefixes = ['v','pub'] # The prefixes used in version files which are not states

class RamSettings( object ):
    """Gets and saves settings used by Ramses.

    To get a setting, just get the corresponding attribute.

    To change a setting temporarily, just set the corresponding attribute. If you want the change to be permanent (i.e. keep the setting for the next sessions), call the save() method.

    By default, settings are saved in a ramses_addons_settings.json file, in the user’s OS specific settings folder:

        Linux: ~/.config/RxLaboratory/Ramses/Config
        Windows: %appdata%/RxLaboratory/Ramses/Config
        MacOS: ?

    There is only one instance of RamSettings, available with the Ramses.instance().settings() method
    """

    _instance = None
    
    def __init__( self ):
        raise RuntimeError("RamSettings can't be initialized with `RamSettings()`, it is a singleton. Call `Ramses.instance().settings()` or `RamSettings.instance()` instead.")

    @classmethod
    def instance( cls ):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

            # Default Values
            cls.online = defaultOnline 
            cls.ramsesClientPath = defaultRamsesClientPath 
            cls.ramsesClientPort = defaultRamsesClientPort 
            cls.logLevel = defaultLogLevel

            cls.defaultOnline = defaultOnline
            cls.defaultRamsesClientPath = defaultRamsesClientPath
            cls.defaultRamsesClientPort = defaultRamsesClientPort
            cls.defaultLogLevel = defaultLogLevel

            # Not Documented: these are not settings to be customized (yet)
            cls.folderNames = folderNames
            cls.defaultStates = defaultStates
            cls.versionPrefixes = versionPrefixes

            # API Settings
            cls.version = version
            cls.apiReferenceUrl = apiReferenceUrl
            cls.addonsHelpUrl = addonsHelpUrl
            cls.generalHelpUrl = generalHelpUrl

            # Set the path to the settings file and temporary folder (os-specific)
            system = platform.system()
            if system == 'Windows':
                cls._folderPath = os.path.expandvars('${APPDATA}/RxLaboratory/Ramses/Config')
                if not os.path.isdir( cls._folderPath ): 
                    os.makedirs( cls._folderPath )
                cls._filePath = cls._folderPath + '/ramses_addons_settings.json'
            else:
                cls._folderPath = ''
                cls._filePath = ''

            # Get settings from file
            if os.path.isfile( cls._filePath ):
                with open(cls._filePath, 'r') as settingsFile:
                    settingsStr = settingsFile.read()
                    settingsDict = json.loads( settingsStr )
                    if 'online' in settingsDict:
                        cls.online = settingsDict['online']
                    if 'clientPath' in settingsDict:
                        cls.ramsesClientPath = settingsDict['clientPath']
                    if 'clientPort' in settingsDict:
                        cls.ramsesClientPort = settingsDict['clientPort']
                    if 'logLevel' in settingsDict:
                        cls.logLevel = settingsDict['logLevel'] 

        return cls._instance

    def folderPath(self):
        return self._folderPath

    def filePath(self):
        return self._filePath

    def save( self ):
        """Saves the current settings to the disk.
        """
        log("I'm saving your settings...")

        settingsDict = {
            'online': self.online,
            'clientPath': self.ramsesClientPath,
            'clientPort': self.ramsesClientPort,
            'logLevel': self.logLevel
        }

        if self._filePath == '':
            raise "Invalid path for the settings, I can't save them, sorry."
        
        with open(self._filePath, 'w') as settingsFile:
            settingsFile.write( json.dumps( settingsDict, indent=4 ) )

        log("Settings saved!")
