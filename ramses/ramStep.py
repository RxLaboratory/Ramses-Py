from .ramObject import RamObject
from .ramses import Ramses
from .ramSettings import RamSettings
from .logger import log, Log, LogLevel
from .file_manager import RamFileManager, decomposeRamsesFileName
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

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

    def commonFolderPath( self ): # Immutable #TODO Check
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """

        if self._folderPath != '':
            return self._folderPath

        # if online
        if Ramses.instance().online():
            stepDict = daemon.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( stepDict ):
                content = stepDict['content']
                self._folderPath = content['folder']

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

    def templatesFolderPath( self ):
        """The path to the template files of this step, relative to the common folder
        Returns:
            str
        """

        project = Ramses.instance().currentProject()
        if project is None:
            log( Log.NoProject, LogLevel.Critical )
            self._folderPath = ''
            return self._folderPath

        projectShortName = project.shortName()
        templatesFolderName = RamSettings.instance().folderNames.stepTemplates
        stepFolder = self.commonFolderPath()

        if stepFolder == "":
            return ""

        return RamFileManager.buildPath( (
            stepFolder,
            projectShortName + "_" + self._shortName + "_" + templatesFolderName
        ))

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
            stepDict = daemon.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( stepDict ):
                content = stepDict['content']
                self._type = content['type']

        splitedPath = self.commonFolderPath().split('/')
        stepContainerFolder = splitedPath[-2]

        if stepContainerFolder == '01-PRE-PROD':
            self._type = StepType.PRE_PRODUCTION
            
        elif stepContainerFolder == '03-POST-PROD':
            self._type = StepType.POST_PRODUCTION
        
        else:  # 02-PROD
            #listdir de 02-PROD
            # pour chaque dossier PROJ_STEP (check si c'est un dossier avec isdir )
            # foldername.split('_')
            # si on obtient trois morceaux : (avec len)
            # le deuxième donne le type (A ou S) -> assetprod ou shotprod

            # si on a pas trouvé, faut aller chercher dans tous les assets
            # for asset in Ramses.instance().currentproject().assets()
                # si self in asset.steps() -> on est un type asset donc return
            # for shot in Ramses.instance().currentproject().shots()
                # si self in shot.steps() -> on est un type shot donc return
            # on sait pas, donc on est jsute "prod"

            self._type = StepType.PRODUCTION


        return self._type

