import os

from .ramObject import RamObject
from .ramses import Ramses
from .logger import log

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

    def __init__( self, stepName, stepShortName, stepFolder='', stepType='' ):
        """     
        Args:
            stepName (str)
            stepShortName (str)
        """
        super().__init__( stepName, stepShortName )
        self._fileType = None
        self._folderPath = stepFolder
        self._type = stepType

    def commonFolderPath( self ): #TODO
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """
        # NOTE :
        # if self._folderPath is not "": return self._folderPath
        # sinon:
            # construire le chemin grace au shortName et chemin du currentproject (Ramses le donne)
            # self._folderPath = résultat de ci dessus (pour pas avoir à reconstruire à chaque fois)
            # return self._folderPath
        pass

    def templatesFolderPath( self ):
        """The path to the template files of this step, relative to the common folder
        Returns:
            str
        """

        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        projectId = Ramses.instance.currentProject().shortName()
        templatesName = Ramses.instance.settings().folderNames.stepTemplates
        stepFolder = self.commonFolderPath()

        if stepFolder == "": return ""
        return stepFolder + '/' + projectId + "_" + self._shortName + "_" + templatesName

    def stepType( self ): #TODO
        """The type of this step, one of RamStep.PRE_PRODUCTION, RamStep.SHOT_PRODUCTION,
            RamStep.ASSET_PRODUCTION, RamStep.POST_PRODUCTION

        Returns:
            enumerated value
        """

        # if self._type != '': return self._type
        # sinon on cherche grace au dossier : le dossier parent de self.commonFolderPath() contient l'info (preprod, postprod, etc)
        # si jamais self.commonFolderPath() est aussi une empty string, on peut rien faire, et on self._type = StepType.ALL puis on return self._type

        return self._type

    # @staticmethod
    # def getFromPath( folderPath ):
    #     from . import Ramses
    #     """Returns a RamStep instance built using the given folder path.
    #         The path can be any file or folder path from the asset
    #         (a version file, a preview file, etc)

    #     Args:
    #         folderPath (str)

    #     Returns:
    #         RamStep
    #     """
    #     if not Ramses.instance:
    #         raise Exception( "Ramses has to be instantiated first." )
    #     if not os.path.isdir( folderPath ):
    #         folderPath = Ramses.instance.currentProject().absolutePath( folderPath ) 
    #         if not os.path.isdir( folderPath ):
    #             log( "The given folder could not be found" )
    #             return None

    #     folderName = os.path.basename( folderPath )

    #     if not Ramses.instance._isRamsesItemFoldername( folderName ):
    #         log( "The given folder does not respect Ramses' naming convention" )
    #         return None

    #         #TODO : pas fini !!

