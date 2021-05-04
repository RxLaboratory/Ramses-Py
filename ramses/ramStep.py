from .ramObject import RamObject
from .ramses import Ramses
from .ramSettings import RamSettings
from .logger import log, Log, LogLevel
from .file_manager import RamFileManager

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
        self._templatesFolder = ''

    def commonFolderPath( self ): # Immutable #TODO
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """

        if self._folderPath != '':
            return self._folderPath

        # if online
        if Ramses.instance().online():
            #TODO demander au démon
            pass

        stepContainerFolder = ''

        if self._type == '':
            self._folderPath = ''
            return self._folderPath

        if self._type == StepType().PRE_PRODUCTION:
            stepContainerFolder = "01-PRE-PROD"
        elif self._type == StepType().PRODUCTION:
            stepContainerFolder = "02-PROD"
        elif self._type == StepType().POST_PRODUCTION:
            stepContainerFolder = "03-POST-PROD"

        project = Ramses.instance().currentProject()
        if project is None:
            log( Log.NoProject, LogLevel.Critical )
            self._folderPath = ''
            return self._folderPath

        projectShortName = project.shortName()
        projectPath = project.folderPath()

        self._folderPath = RamFileManager.buildPath( (
            projectPath,
            stepContainerFolder,
            projectShortName + "_" + self.shortName()
        ) ) # /path/to/ProjectID/02-PROD/ProjectID_stepID

        return self._folderPath

    def templatesFolderPath( self ): # Immutable
        """The path to the template files of this step, relative to the common folder
        Returns:
            str
        """

        if self._templatesFolder != '':
            return self._templatesFolder

        project = Ramses.instance().currentProject()
        if project is None:
            log( Log.NoProject, LogLevel.Critical )
            return ''

        projectShortName = project.shortName()
        templatesFolderName = RamSettings.instance().folderNames.stepTemplates
        stepFolder = self.commonFolderPath()

        if stepFolder == '':
            return ''

        self._templatesFolder = RamFileManager.buildPath((
            stepFolder,
            projectShortName + "_" + self._shortName + "_" + templatesFolderName
        ))

        return self._templatesFolder

    def stepType( self ): #Immutable #TODO
        """The type of this step, one of RamStep.PRE_PRODUCTION, RamStep.SHOT_PRODUCTION,
            RamStep.ASSET_PRODUCTION, RamStep.POST_PRODUCTION

        Returns:
            enumerated value
        """
        if self._type != "":
            return self._type

        if self.commonFolderPath() == "":
            return ""

        # if online
        if Ramses.instance().online():
            #TODO demander au démon
            pass

        splitedPath = self.commonFolderPath().split('/')
        stepContainerFolder = splitedPath[-2]

        if stepContainerFolder == '01-PRE-PROD':
            self._type = StepType.PRE_PRODUCTION
        elif stepContainerFolder == '02-PROD':
            #TODO
            # Grâce à self._shortName
            # Chercher dans assets si on trouve un asset qui utilise ce shortname (utiliser decomposeRamsesFileName)
            # sinon chercher dans shots,
            # et on saura si on est asset prod ou shot prod
            # et seulement en tout dernier on mettra prod si rien d'autre
            self._type = StepType.PRODUCTION
        elif stepContainerFolder == '03-POST-PROD':
            self._type = StepType.POST_PRODUCTION

        return self._type

