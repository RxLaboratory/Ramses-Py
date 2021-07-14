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

from .ram_pipefile import RamPipeFile

class RamPipe:
    """A pipe which connects two steps together in the production pipeline.
        The pipe goes from the output step (which exports data into a specific file type)
        to the input step (which imports that data)."""

    @staticmethod
    def fromDict( pipeDict ):
        """Builds a RamPipe from dict like the ones returned by the RamDaemonInterface"""

        pipeFiles = []

        if 'pipeFiles' in pipeDict:
            for pipe in pipeDict['pipeFiles']:
                pipeFiles.append(
                    RamPipeFile.fromDict(pipe)
                )

        return RamPipe(
            pipeDict['inputStepShortName'],
            pipeDict['outputStepShortName'],
            pipeFiles
        )

    def __init__( self, inputStepShortName, outputStepShortName, pipeFiles ):
        """

        Args:
            inputStepShortName (str)
            outputStepShortName (str)
            fileType (str)
            colorSpace (str)
        """
        self._inputStepShortName = inputStepShortName
        self._outputStepShortName = outputStepShortName
        self._pipeFiles = pipeFiles

    def inputStepShortName( self ):
        """The short name of the input step

        Returns:
            str
        """
        return self._inputStepShortName

    def outputStepShortName( self ):
        """The short name of the output step

        Returns:
            str
        """
        return self._outputStepShortName

    def pipeFiles( self ):
        return self._pipeFiles