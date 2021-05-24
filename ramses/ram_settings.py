import os
import platform
import json
from .constants import FolderNames, LogLevel
from .logger import log

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

            # Wether to always try to (re)connect to the Daemon if offline.
            cls.online = cls.defaultOnline = True 
            # Location of the Ramses Client executable file (.exe on Windows, .app on MacOS, .appimage or binary on Linux)
            cls.ramsesClientPath =  cls.defaultRamsesClientPath = ""
            # Listening port of the Ramses Daemon
            cls.ramsesClientPort = cls.defaultRamsesClientPort = 18185
            # Minimum Log level printed when logging information
            cls.logLevel = cls.defaultLogLevel = LogLevel.Info
            # Timeout before auto incrementing a file, in minutes
            cls.autoIncrementTimeout = cls.defaultAutoIncrementTimeout = 120
            # The folder containing all ramses files
            cls.defaultRamsesFolderPath = os.path.expanduser("~/Ramses")

            # The default ramses folder may be in Documents (in Maya....), adjust
            if cls.defaultRamsesFolderPath.endswith("Documents/Ramses"):
                cls.defaultRamsesFolderPath = cls.defaultRamsesFolderPath.replace("Documents/Ramses", "Ramses")           
            cls.ramsesFolderPath = cls.defaultRamsesFolderPath

            # Not Documented: these are not settings to be customized (yet)

            cls.folderNames = FolderNames()
            cls.versionPrefixes = ['v','pub'] # The prefixes used in version files which are not states

            # API Settings
            cls.version = version = "0.0.1-dev"
            cls.apiReferenceUrl = "https://ramses-docs.rainboxlab.org/dev/add-ons-reference/"
            cls.addonsHelpUrl = "https://ramses-docs.rainboxlab.org/addons/"
            cls.generalHelpUrl = "https://ramses-docs.rainboxlab.org/"

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
                    if 'autoIncrementTimeout' in settingsDict:
                        cls.autoIncrementTimeout = settingsDict['autoIncrementTimeout']
                    if 'ramsesFolderPath' in settingsDict:
                        cls.ramsesFolderPath = settingsDict['ramsesFolderPath']

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
            'logLevel': self.logLevel,
            'autoIncrementTimeout': self.autoIncrementTimeout,
            'ramsesFolderPath': self.ramsesFolderPath,
        }

        if self._filePath == '':
            raise ("Invalid path for the settings, I can't save them, sorry.")
        
        with open(self._filePath, 'w') as settingsFile:
            settingsFile.write( json.dumps( settingsDict, indent=4 ) )

        log("Settings saved!")
