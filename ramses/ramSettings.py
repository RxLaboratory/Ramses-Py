class FolderNames():
    preview = "_preview"
    versions = "_versions"
    publish = "_published"
    userConfig = "Config"

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

    def save( self ): #TODO
        """Saves the current settings to the disk.
        """
        pass

