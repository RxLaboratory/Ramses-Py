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
from .file_info import RamFileInfo
from .daemon_interface import RamDaemonInterface
from .file_manager import RamFileManager
from .logger import log
from .utils import removeDuplicateObjectsFromList
from .ram_settings import RamSettings
from .ram_object import RamObject
from .ram_asset import RamAsset
from .constants import StepType, LogLevel

DAEMON = RamDaemonInterface.instance()
SETTINGS = RamSettings.instance()

class RamProject( RamObject ):
    """A project handled by Ramses. Projects contains general items, assets and shots."""

    @staticmethod
    def fromPath( path ):
        """Creates a project object from any path, trying to get info from the given path"""
        from .ramses import Ramses
        RAMSES = Ramses.instance()

        uuid = DAEMON.uuidFromPath( path, "RamProject" )

        if uuid != "":
            return RamProject(uuid)

        # Try from the file name
        nm = RamFileInfo()
        nm.setFilePath( path )
        if nm.project != '':
            return RAMSES.project( nm.project )

        log( "The given path does not belong to a project", LogLevel.Debug )
        return None

    def __init__( self, uuid="", data = None, create=False ):
        """
        Args:
            uuid (str)
        """
        super(RamProject, self).__init__( uuid, data, create, "RamProject" )

    def width( self ):
        """
        Returns:
            int
        """

        return self.get("width", 1920)

    def height( self ):
        """
        Returns:
            int
        """

        return self.get("height", 1080)

    def framerate( self ):
        """
        Returns:
            float
        """

        return self.get("framerate", 24.0)

    def absolutePath( self, relativePath="" ):
        """Builds an absolute path from a path relative to the project path

        Args:
            relativePath (str)

        Returns:
            str
        """
        return RamFileManager.buildPath((
            self.folderPath(),
            relativePath
        ))

    def adminPath( self ):
        """Returns the path of the Admin folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.admin
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""
        
        return thePath

    def preProdPath( self ):
        """Returns the path of the PreProd folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.preProd
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""

        return thePath

    def prodPath( self ):
        """Returns the path of the Prod folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.prod
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""

        return thePath

    def postProdPath( self ):
        """Returns the path of the PostProd folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.postProd
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""

        return thePath

    def assetsPath( self, assetGroup='' ):
        """Returns the path of the Assets folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.assets,
            assetGroup
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""
        
        return thePath

    def shotsPath( self ):
        """Returns the path of the Shots folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.shots
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""
        
        return thePath

    def exportPath( self ):
        """Returns the path of the Export folder (creates it if it does not exist yet)"""

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            SETTINGS.folderNames.export
        ))

        if not os.path.isdir( thePath ):
            try:
                os.makedirs( thePath )
            except:
                return ""
        
        return thePath

    def assets( self, assetGroup=None ):
        """Available assets in this project and group.
        If groupName is an empty string, returns all assets.

        Args:
            groupName (str, optional): Defaults to "".

        Returns:
            list of RamAsset
        """

        groupUuid = RamObject.getUuid(assetGroup)
        return DAEMON.getAssets(self.uuid(), groupUuid)

    def assetGroups( self ):
        """Available asset groups in this project

        Returns:
            list of RamAssetGroup
        """
        
        return DAEMON.getAssetGroups(self.uuid())

    def shots( self, nameFilter = "*", sequence = None ):
        """Available shots in this project

        Args:
            nameFilter

        Returns:
            list of RamShot
        """

        groupUuid = RamObject.getUuid(sequence)
        shots = DAEMON.getShots(self.uuid(), groupUuid)

        if nameFilter == "*" or nameFilter == "":
            return shots

        result = []
        
        for shot in shots:
            if not nameFilter in shot.name():
                continue
            if not nameFilter in shot.shortName():
                continue
            result.append( shot )

        return result

    def sequences( self ):
        """The sequences of this project"""
        
        return DAEMON.getSequences(self.uuid())

    def step(self, shortName):
        """
        Gets a step using its shortName
        
        return:
            RamStep
        """
        stps = self.steps()
        for s in stps:
            if s.shortName() == shortName:
                return s
        return None

    def steps( self, stepType=StepType.ALL ):
        """Available steps in this project. Use type to filter the results.
            One of: RamStep.ALL, RamStep.ASSET_PODUCTION, RamStep.SHOT_PRODUCTION, RamStep.PRE_PRODUCTION, RamStep.PRODUCTION, RamStep.POST_PRODUCTION.
            RamStep.PRODUCTION represents a combination of SHOT and ASSET

        Args:
            typeStep (enumerated value, optional): Defaults to RamStep.ALL.

        Returns:
            list of RamStep
        """
        
        return DAEMON.getSteps(self.uuid(), stepType)

    def pipes( self ):
        """Available pipes in this project

        Returns:
            list of RamPipe
        """
        
        return DAEMON.getPipes(self.uuid())

    def _getAssetsInFolder(self, folderPath, assetGroup=None ):
        """lists and returns all assets in the given folder"""
        assetList = []
        
        for foundFile in os.listdir( folderPath ):
            # look in subfolder
            if os.path.isdir( folderPath + '/' + foundFile ):
                assets = self._getAssetsInFolder( folderPath + '/' + foundFile, assetGroup )
                assetList = assetList + assets
            
            # Get Asset
            asset = RamAsset.fromPath( folderPath + '/' + foundFile )
            if asset is None:
                continue
            if asset.group() == assetGroup:
                assetList.append( asset )

        return removeDuplicateObjectsFromList( assetList )
