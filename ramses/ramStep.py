from .ramObject import RamObject


class RamStep( RamObject ):
    """A step in the production of the shots or assets of the project.
    """

    def __init__( self, stepName, stepShortName ):
        """     
        Args:
            stepName (str)
            stepShortName (str)
        """
        self.name = stepName
        self.shortName = stepShortName

    def commonFolderPath( self ): #TODO
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """
        pass

    def templatesFolderPath( self ): #TODO
        """The path to the template files of this step, relative to the common folder
        Returns:
            str
        """
        pass

    def typeStep( self ): #TODO
        """The type of this step, one of RamStep.PRE_PRODUCTION, RamStep.SHOT_PRODUCTION,
            RamStep.ASSET_PRODUCTION, RamStep.POST_PRODUCTION

        Returns:
            enumerated value
        """
        pass
