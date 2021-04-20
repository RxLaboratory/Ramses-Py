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

    autoConnect = True
    # Wether to always try to (re)connect to the Daemon if offline.

    ramsesClientPath = ""
    # Location of the Ramses Client executable file (.exe on Windows, .app on MacOS, .appimage or binary on Linux)

    ramsesClientPort = 18185
    # Listening port of the Ramses Daemon

    folderPath = ""
    # Read-only. The folder path to the settings (os-specific)

    filePath = ""
    # Read-only. The file path to the settings (os-specific)

    def save( self ): #TODO
        """Saves the current settings to the disk.
        """
        pass
