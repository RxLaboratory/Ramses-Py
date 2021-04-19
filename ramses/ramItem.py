from ramses.ramObject import RamObject

class RamItem(RamObject):
    """
    Base class for RamAsset and RamShot.
    An item of the project, either an asset or a shot.
    """

    def __init__(self, itemName, itemShortName, itemFolder=""):
        """
        @param: 

        """