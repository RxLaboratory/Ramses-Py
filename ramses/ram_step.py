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

    @staticmethod
    def fromPath( path ):
        """Creates a step from any path, if possible
        by extracting step info from the path"""
        from .ram_project import RamProject

        project = RamProject.fromPath( path )
        if project is None:
            return None
        
        pathInfo = RamFileManager.decomposeRamsesFilePath( path )
        return project.step( pathInfo['step'] )

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

        stepType = self.type()

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

        pathInfo = RamFileManager.decomposeRamsesFilePath( stepFolder )
        projectShortName = pathInfo['project']

        self._templatesFolder = RamFileManager.buildPath((
            stepFolder,
            projectShortName + "_G_" + self._shortName + "_" + FolderNames.stepTemplates
        ))

        return self._templatesFolder

    def stepType( self ): #Immutable
        """The type of this step, one of StepType.PRE_PRODUCTION, StepType.SHOT_PRODUCTION,
            StepType.ASSET_PRODUCTION, StepType.POST_PRODUCTION

        Returns:
            enumerated value
        """

        from .ram_project import RamProject

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
        project = RamProject.fromPath( stepFolder )
        
        if RamFileManager.isAssetStep( self.shortName(), project.assetsPath() ):
            self._type = StepType.ASSET_PRODUCTION
            return self._type

        if RamFileManager.isShotStep( self.shortName(), project.shotsPath() ):
            self._type = StepType.SHOT_PRODUCTION
            return self._type


        return ""

