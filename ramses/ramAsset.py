from ramses.ramItem import RamItem

class RamAsset(RamItem):

    def __init__(self, assetName, assetShortName):
        """
        @param: {assetName} str : assetName
        @param: {assetShortName} str : assetShortName
        """
        super().__init__()
        self.__assetName = assetName
        self.__assetShortName = assetShortName

    def tags(self):
        """
        Some tags describing the asset.
        return list of string
        """
        return self.tags

    def group(self):
        """
        The group containing this asset.
        return string
        """
        return self.group

    @staticmethod
    def getFromPath(self, folderPath):
        """
        Returns a RamAsset instance built using the given path.
        The path can be any file or folder path from the asset 
        (a version file, a preview file, etc)
        @param: {folderPath} str 
        @return: RamAsset
        """
        pass

    