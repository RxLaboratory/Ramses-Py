from ramses.ramItem import RamItem

class RamShot(RamItem):
    """ A shot """

    def __init__(self, shotName, shotShortName):
        """
        @param: {shotName} str : shotName
        @param: {shotShortName} str : shotShortName
        """
        super().__init__()
        self.__shotName = shotName
        self.__shotShortName = shotShortName

    def duration(self):
        """
        The shot duration, in seconds
        return float
        """
        pass

    @staticmethod
    def getFromPath(self, folderPath):
        """
        Returns a RamShot instance built using the given folder path.
        The path can be any file or folder path from the asset
        (a version file, a preview file, etc)
        @param: {folderPath} str
        @return: RamShot
        """
        pass