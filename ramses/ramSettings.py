from .ramState import RamState

class FolderNames():
    preview = "_preview"
    versions = "_versions"
    publish = "_published"
    userConfig = "Config"
    stepTemplates = "Templates"

class RamSettings:
    """Gets and saves settings used by Ramses.

    To get a setting, just get the corresponding attribute.

    To change a setting temporarily, just set the corresponding attribute. If you want the change to be permanent (i.e. keep the setting for the next sessions), call the save() method.

    By default, settings are saved in a ramses_addons_settings.json file, in the user’s OS specific settings folder:

        Linux: ~/.config/RxLaboratory/Ramses/
        Windows: %appdata%/RxLaboratory/Ramses/
        MacOS: ?

    There is only one instance of RamSettings, available with the Ramses.instance.settings() method
    """
    
    def __init__( self ):
        # TODO Load from the settings file saved previously with save()
        self.autoConnect = True # Wether to always try to (re)connect to the Daemon if offline.
        self.ramsesClientPath = "" # Location of the Ramses Client executable file (.exe on Windows, .app on MacOS, .appimage or binary on Linux)
        self.ramsesClientPort = 18185 # Listening port of the Ramses Daemon
        self.folderPath = "" # Read-only. The folder path to the settings (os-specific)
        self.filePath = "" # Read-only. The file path to the settings (os-specific)

        # Not Documented: these are not settings to be customized (yet)
        self.folderNames = FolderNames()
        self.defaultStates = [
            RamState("No", "NO", 1.0, [25,25,25]), # Very dark gray
            RamState("To Do", "TODO", 0.0, [85, 170, 255]), # Blue
            RamState("Work in progress", "WIP", 0.5,  [255,255,127]), # Light Yellow
            RamState("OK", "OK", 1.0, [0, 170, 0]), # Green
        ]

    def save( self ): #TODO
        """Saves the current settings to the disk.
        """
        pass

