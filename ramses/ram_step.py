# -*- coding: utf-8 -*-

import os

from .ram_object import RamObject
from .ramses import Ramses
from .logger import log
from .constants import StepType, FolderNames, Log, LogLevel
from .file_manager import RamFileManager
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamStep( RamObject ):
    """A step in the production of the shots or assets of the project."""

    @staticmethod
    def fromDict( stepDict ):
        """Builds a RamStep from dict like the ones returned by the RamDaemonInterface"""

        s = RamStep(
            stepDict['name'],
            stepDict['shortName'],
            stepDict['folder'],
            stepDict['type']
        )
        return s

    # project is undocumented and used to improve performance, when called from a RamProject
    @staticmethod
    def fromPath( path, project=None ):
        """Creates a step from any path, if possible
        by extracting step info from the path"""
        from .ram_project import RamProject

        if project is None:
            project = RamProject.fromPath( path )
            if project is None:
                return None

        pathInfo = RamFileManager.decomposeRamsesFilePath( path )
        # To improve perf, pass other information than just step short name to the method
        return project.step( pathInfo['step'], pathInfo['type'] )

    def __init__( self, stepName, stepShortName, stepFolder='', stepType=StepType.ALL ):
        """     
        Args:
            stepName (str)
            stepShortName (str)
        """
        super(RamStep, self).__init__( stepName, stepShortName )
        self._folderPath = stepFolder
        self._type = stepType
        self._templatesFolder = ''
        self._project = None
        self._projectShortName = ""
        self._inputPipes = []
        self._outputPipes = []

    def folderPath( self ): # Immutable
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """

        if self._folderPath != '':
            return self._folderPath

        # if online
        if Ramses.instance().online():
            reply = daemon.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._folderPath = reply['content']['folder']
                if self._folderPath != '':
                    return self._folderPath

        stepType = self.stepType()

        if stepType == '' or stepType == StepType.ALL:
            self._folderPath = ''
            return self._folderPath
     
        project = Ramses.instance().currentProject()
        if project is None:
            log( Log.NoProject, LogLevel.Critical )
            self._folderPath = ''
            return self._folderPath

        stepContainerFolder = ''

        if stepType == StepType.PRE_PRODUCTION:
            stepContainerFolder = project.preProdPath()
        elif stepType == StepType.PRODUCTION or stepType == StepType.SHOT_PRODUCTION or stepType == StepType.ASSET_PRODUCTION:
            stepContainerFolder = project.prodPath()
        elif stepType == StepType.POST_PRODUCTION:
            stepContainerFolder = project.postProdPath()

        projectShortName = project.shortName()

        self._folderPath = RamFileManager.buildPath( (
            stepContainerFolder,
            projectShortName + "_G_" + self.shortName()
        ) ) # /path/to/ProjectID/02-PROD/ProjectID_G_stepID

        return self._folderPath

    def inputPipes( self ): # Immutable
        if len(self._inputPipes) > 0:
            return self._inputPipes

        project = self.project()
        if project is None:
            return self._outputPipes

        pipes = project.pipes()

        for pipe in pipes:
            if pipe.inputStepShortName() == self.shortName():
                self._inputPipes.append(pipe)

        return self._inputPipes
    
    def outputPipes( self ): # Immutable
        if len(self._outputPipes) > 0:
            return self._outputPipes

        project = self.project()
        if project is None:
            return self._outputPipes

        pipes = project.pipes()

        for pipe in pipes:
            if pipe.outputStepShortName() == self.shortName():
                self._outputPipes.append(pipe)

        return self._outputPipes

    def templatesFolderPath( self ): # Immutable
        """The path to the template files of this step
        Returns:
            str
        """

        if self._templatesFolder != '':
            return self._templatesFolder

        
        stepFolder = self.folderPath()

        if stepFolder == '':
            return ''

        projectShortName = self.projectShortName()
        if projectShortName == '':
            return ''

        self._templatesFolder = RamFileManager.buildPath((
            stepFolder,
            projectShortName + "_G_" + self._shortName + "_" + FolderNames.stepTemplates
        ))

        if not os.path.isdir(self._templatesFolder):
            os.makedirs(self._templatesFolder)

        return self._templatesFolder

    def templatesPublishPath( self ):
        """The path to the folder where templates are published"""
        templatesFolderPath = self.templatesFolderPath()
        if templatesFolderPath == '':
            return ''

        folder = RamFileManager.buildPath((
            templatesFolderPath,
            FolderNames.publish
        ))

        if not os.path.isdir(folder):
            os.makedirs(folder)

        return folder

    def templatesPublishFilePaths( self ):
        templatesPublishPath = self.templatesPublishPath()
        if templatesPublishPath == '':
            return []

        return RamFileManager.getRamsesFiles( templatesPublishPath )

    def stepType( self ): #Immutable
        """The type of this step, one of StepType.PRE_PRODUCTION, StepType.SHOT_PRODUCTION,
            StepType.ASSET_PRODUCTION, StepType.POST_PRODUCTION

        Returns:
            enumerated value
        """

        if self._type != "":
            return self._type

        # if online
        if Ramses.instance().online():
            reply = daemon.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                self._type = content['type']

        # If offline and don't have the path, can't do anything
        stepFolder = self.folderPath()
        if stepFolder == "":
            return ""

        # Check the container folder
        stepContainerFolder = os.path.dirname( stepFolder )

        if stepContainerFolder == FolderNames.preProd:
            self._type = StepType.PRE_PRODUCTION
            return self._type
            
        if stepContainerFolder == FolderNames.postProd:
            self._type = StepType.POST_PRODUCTION
            return self._type

        # Get info from the project
        project = self.project()
        if project is None:
            return ''
        
        if RamFileManager.isAssetStep( self.shortName(), project.assetsPath() ):
            self._type = StepType.ASSET_PRODUCTION
            return self._type

        if RamFileManager.isShotStep( self.shortName(), project.shotsPath() ):
            self._type = StepType.SHOT_PRODUCTION
            return self._type


        return ""

    def project(self): # Immutable
        """Returns the project this step belongs to"""
        from .ram_project import RamProject

        if self._project is not None:
            return self._project

        folderPath = self.folderPath()
        if folderPath == '':
            return None

        self._project = RamProject.fromPath( folderPath )
        return self._project

    def projectShortName(self): # Immutable
        """Returns the short name of the step this item belongs to"""

        if self._projectShortName != "":
            return self._projectShortName

        if self._project is not None:
            self._projectShortName = self._project.shortName()
            return self._projectShortName

        folderPath = self.folderPath()
        if folderPath == '':
            return ''

        folderInfo = RamFileManager.decomposeRamsesFilePath(folderPath)
        if folderInfo is None:
            return ''

        self._projectShortName = folderInfo['project']
        return self._projectShortName