from .ramObject import RamObject
from .ramses import Ramses

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

        dir = ""

        if self._type == "":
            return ""
        elif self._type == StepType().PRE_PRODUCTION:
            dir = "01-PRE-PROD"
        elif self._type == StepType().PRODUCTION:
            dir = "02-PROD"
        elif self._type == StepType().POST_PRODUCTION:
            dir = "03-POST-PROD"

        if self._folderPath != "":
            return self._folderPath
        else:
            name = Ramses.instance().currentProject().shortName()
            path = Ramses.instance().currentProject().folderPath()
            self._folderPath = path + dir + "/" + name + "_" + self.shortName()
            return self._folderPath


    def templatesFolderPath( self ):
        """The path to the template files of this step, relative to the common folder
        Returns:
            str
        """

        projectId = Ramses.instance().currentProject().shortName()
        templatesName = Ramses.instance().settings().folderNames.stepTemplates
        stepFolder = self.commonFolderPath()

        if stepFolder == "": return ""
        return stepFolder + '/' + projectId + "_" + self._shortName + "_" + templatesName

    def stepType( self ): #TODO
        """The type of this step, one of RamStep.PRE_PRODUCTION, RamStep.SHOT_PRODUCTION,
            RamStep.ASSET_PRODUCTION, RamStep.POST_PRODUCTION

        Returns:
            enumerated value
        """
        if self._type != "":
            return self._type
        elif self.commonFolderPath() == "":
            return ""
        else:
            splitedPath = self.commonFolderPath().split('/')
            self._type = splitedPath[-2]

        return self._type

