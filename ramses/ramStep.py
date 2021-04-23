from .ramObject import RamObject

class StepType():
    PRE_PRODUCTION = 'PRE_PRODUCTION'
    ASSET_PRODUCTION = 'ASSET_PRODUCTION'
    SHOT_PRODUCTION = 'SHOT_PRODUCTION'
    POST_PRODUCTION = 'POST_PRODUCTION'
    ALL = 'ALL' # tous
    PRODUCTION = 'PRODUCTION' # asset et shot

class RamStep( RamObject ):
    """A step in the production of the shots or assets of the project.
    """

    def __init__( self, stepName, stepShortName ):
        """     
        Args:
            stepName (str)
            stepShortName (str)
        """
        super().__init__( stepName, stepShortName )
        self.fileType = None

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

    def stepType( self ): #TODO
        """The type of this step, one of RamStep.PRE_PRODUCTION, RamStep.SHOT_PRODUCTION,
            RamStep.ASSET_PRODUCTION, RamStep.POST_PRODUCTION

        Returns:
            enumerated value
        """
        pass

    @staticmethod
    def getFromPath( folderPath ):
        """Returns a RamStep instance built using the given folder path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            folderPath (str)

        Returns:
            RamStep
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        if not os.path.isdir( folderPath ):
            folderPath = Ramses.instance.currentProject().getAbsolutePath( folderPath )  # A vérifier...
            if not os.path.isdir( folderPath ):
                log( "The given folder could not be found" )
                return None

        folderName = os.path.basename( folderPath )

        if not Ramses.instance._isRamsesItemFoldername( folderName ):
            log( "The given folder does not respect Ramses' naming convention" )
            return None

            #TODO : pas fini !!

