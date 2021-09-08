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

import os, re
from .constants import ItemType
from .utils import intToStr
from .ram_settings import RamSettings

# Keep the settings at hand
settings = RamSettings.instance()

class RamNameManager():
    """A class to help generating filenames or getting data from filenames"""

    # Cache stuff
    __nameRe = None # The regexp to handle names. Initialized the first time it's needed

    def __init__(self):
        
        self.__init()

        self.__stateShortNames = () # The list of state short names. Initialized the first time it's needed

        # Other private attributes
        self.__fileName = ""

    def __init( self ):
        """Private method to (re)initialize attributes except cache"""
        self.project = ""
        self.ramType = ""
        self.shortName = ""
        self.step = ""
        self.resource = ""
        self.state = ""
        self.version = -1
        self.extension = ""

    def __getRamsesNameRegEx( self ):
        """Private method to get a Regex to check if a file matches Ramses' naming convention."""

        if RamNameManager.__nameRe is not None:
            return RamNameManager.__nameRe

        regexStr = self.___getVersionRegExStr()

        regexStr = '^([a-z0-9+-]{1,10})_(?:([ASG])_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+-]{1,10}))(?:_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+-]{1,10}))?(?:_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+\\s-]+))?(?:_(' + regexStr + ')?([0-9]+))?(?:\\.([a-z0-9.]+))?$'

        regex = re.compile(regexStr, re.IGNORECASE)

        RamNameManager.__nameRe = regex
        return regex

    def ___getVersionRegExStr( self ):
        """Private method to get a Regex str that can be used to identify version blocks.

        A version block is composed of an optional version prefix and a version number.
        'wip002', 'v10', '1002' are version blocks; '002wip', '10v', 'v-10' are not.\n
        Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ).
        """

        from .ramses import Ramses
        ramses = Ramses.instance()

        if len( self.__stateShortNames ) == 0:
            self.__stateShortNames = settings.versionPrefixes
            states = ramses.states()
            for state in states:
                self.__stateShortNames.append( state.shortName() )

        return '|'.join( self.__stateShortNames )

    def originalFileName( self ):
        """Gets the original filename without any change"""
        return self.__fileName

    def fileName( self ):
        """Constructs and returns the fileName"""

        nameList = []

        nameList.append( self.project )

        if self.ramType != '':
            nameList.append( self.ramType )

        if self.ramType in (ItemType.ASSET, ItemType.SHOT) and self.shortName != "":
            nameList.append( self.shortName )

        if self.step != "":
            nameList.append( self.step )

        if self.ramType == ItemType.GENERAL and self.shortName != "" and self.shortName != self.step:
            nameList.append( self.shortName )

        if self.resource != '':
            nameList.append( self.resource )

        if self.version != -1:
            v = self.state + intToStr(self.version)
            nameList.append( v )

        ramsesFileName = '_'.join( nameList )
        
        if self.extension != '':
            if not self.extension.startswith('.'):
                self.extension = '.' + self.extension
            ramsesFileName = ramsesFileName + self.extension

        return ramsesFileName

    def setFileName( self, name ):
        """Sets the filename and parses data from it. Returns boolean for success"""
        self.__init()

        splitRamsesName = re.match(self.__getRamsesNameRegEx(), name)

        if splitRamsesName == None:
            return False

        self.project = splitRamsesName.group(1)
        self.ramType = splitRamsesName.group(2)

        if self.ramType in (ItemType.ASSET, ItemType.SHOT):
            self.shortName = splitRamsesName.group(3)
            if splitRamsesName.group(4) is not None:
                self.step = splitRamsesName.group(4)
        else:
            self.step = splitRamsesName.group(3)
            if splitRamsesName.group(4) is not None:
                self.shortName = splitRamsesName.group(4)

        if splitRamsesName.group(5) is not None:
            self.resource = splitRamsesName.group(5)
            self.resource = re.sub( '\+restored-v\d+\+', "", self.resource)
        
        if splitRamsesName.group(6) is not None:
            self.state = splitRamsesName.group(6)

        if splitRamsesName.group(7) is not None:
            self.version = int ( splitRamsesName.group(7) )

        if splitRamsesName.group(8) is not None:
            self.extension = splitRamsesName.group(8)

        return True

    def setFilePath( self, path ):
        """Tries to get the maximum information from the path"""

        from .file_manager import RamFileManager

        originalPath = path
        name = os.path.basename( path )

        # First get information specific to files or innest folder, won't be found in parent folders:
        self.setFileName( name )

        # If this is a project path, let's just use the project short name
        if RamFileManager.isProjectFolder( path):
            self.project = os.path.basename(path)
            return

        # Move up to the parent folder
        path = os.path.dirname(path)
        name = os.path.basename(path)

         # Move up the tree until we've found something which can be decomposed
        while name != '':
            # If we've found all the info, we can return
            if self.project != '' and self.ramType != '' and self.shortName != '' and self.step != '':
                return

            # Try to get more info from the folder name
            nm = RamNameManager()
            if nm.setFileName( name ):
                if self.project == '':
                    self.project = nm.project
                if self.ramType == '':
                    self.ramType = nm.ramType
                if self.shortName == '':
                    self.shortName = nm.shortName
                if self.step == '':
                    self.step = nm.step

            # We got to the project folder, no need to continue
            if RamFileManager.isProjectFolder( path ):
                # The project short name can still be found from the project folder
                if self.project == '':
                    self.project = name
                return

            # Move up to the parent folder
            path = os.path.dirname(path)
            name = os.path.basename(path)
        
        # We really need to find the project. If not found, try to decompose names in files inside the given path
        if self.project == '':
            if os.path.isfile(originalPath):
                originalPath = os.path.dirname(originalPath)

            if not os.path.isdir( originalPath ):
                return

            for f in os.listdir(originalPath):
                filePath = RamFileManager.buildPath(( originalPath, f ))
                if not os.path.isfile(filePath):
                    continue
                nm = RamNameManager()
                nm.setFileName( name )
                if nm.project == '':
                    continue
                
                self.project = nm.project
                break

    def copy( self ):
        """Returns a copy of the current instance"""

        nm = RamNameManager()
        nm.project = self.project
        nm.ramType = self.ramType
        nm.shortName = self.shortName
        nm.step = self.step
        nm.resource = self.resource
        nm.state = self.state
        nm.version = self.version
        nm.extension = self.extension
        nm.__stateShortNames = self.__stateShortNames
        nm.__fileName = nm.__fileName

        return nm