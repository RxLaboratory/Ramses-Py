# -*- coding: utf-8 -*-

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import os
from platform import version
from .file_info import RamFileInfo
from .ram_object import RamObject
from .ramses import Ramses
from .logger import log
from .constants import StepType, FolderNames, Log, LogLevel
from .file_manager import RamFileManager
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
DAEMON = RamDaemonInterface.instance()

class RamStep( RamObject ):
    """A step in the production of the shots or assets of the project."""

    @staticmethod
    def fromDict( objectDict ):
        """Builds a RamStep from dict like the ones returned by the RamDaemonInterface"""

        s = RamStep(
            objectDict['name'],
            objectDict['shortName'],
            objectDict['folder'],
            objectDict['type']
        )
        if 'color' in objectDict:
            s._color = objectDict['color'] # pylint: disable=protected-access
        if 'publishSettings' in objectDict:
            s._publishSettings = objectDict['publishSettings'] # pylint: disable=protected-access
        return s

    @staticmethod
    def fromString( objStr ):
        obj = RamObject.fromString( objStr )
        step = RamStep( obj.name(), obj.shortName() )

        # try to get from current project
        proj = Ramses.instance().currentProject()
        if proj is None:
            return step
        
        s = proj.step( step.shortName() )
        if s is None:
            return step
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

        nm = RamFileInfo()
        nm.setFilePath( path )

        # To improve perf, pass other information than just step short name to the method
        return project.step( nm.step, nm.ramType )

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
        self._color = None
        self._publishSettings = ""

    def color( self ): # Immutable
        if self._color is not None:
            return self._color

        color = ( 165/255.0, 38/255.0, 196/255.0 )

        # if online
        if Ramses.instance().online():
            reply = DAEMON.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                self._color = content['color']
                color = self._color

        return color

    def folderPath( self ): # Immutable
        """The absolute path to the folder containing the common files for this step

        Returns:
            str
        """

        if self._folderPath != '':
            return self._folderPath

        # if online
        if Ramses.instance().online():
            reply = DAEMON.getStep( self._shortName )
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
            FolderNames.stepTemplates
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

    def templatesPublishedVersionFolderPaths( self ):
        templatesPublishPath = self.templatesPublishPath()
        
        versionFolders = []

        for f in os.listdir(templatesPublishPath):
            folderPath = RamFileManager.buildPath(( templatesPublishPath, f ))
            if not os.path.isdir(folderPath): continue
            versionFolders.append( folderPath )

        versionFolders.sort(key=RamFileManager._publishVersionFoldersSorter)

        return versionFolders

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
            reply = DAEMON.getStep( self._shortName )
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

        nm = RamFileInfo()
        nm.setFilePath( folderPath )
        if nm.project == '':
            return ''

        self._projectShortName = nm.project
        return self._projectShortName

    def publishSettings(self): # Immutable
        """Returns the publish settings, as a string,
        which should be a yaml document, according to the Ramses guidelines.
        But this string is user-defined and can be anything set in the Ramses Client."""
        if self._publishSettings != "":
            return self._publishSettings

        # if online
        if Ramses.instance().online():
            reply = DAEMON.getStep( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                if "publishSettings" in content:
                    self._publishSettings = content['publishSettings']

        return self._publishSettings

    def setPublishSettings(self, settings):
        if not Ramses.instance().online():
            return
        DAEMON.setPublishSettings(
            self.shortName(),
            self.name(),
            settings
        )