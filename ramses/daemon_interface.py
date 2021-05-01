import socket
import json
from .logger import log, LogLevel, Log

class RamDaemonInterface():
    """The Class used to communicate with the Ramses Daemon

    Attributes:
        port: int.
            The listening port of the daemon
        online: bool (read-only).
            True if the Daemon is available
    """

    @staticmethod
    def checkReply( obj ):
        return obj['accepted'] and obj['success'] and obj['content'] is not None

    def __init__(self, port = 18185):
        """
        Args:
            port: int.
        """
        self.port = port
        self.address = 'localhost'

    def online(self):
        return self.__testConnection()

    def __buildQuery(self, query):
        """Builds a query from a list of args

        Args:
            query: str or tuple.
                If query is a str, it is returned as is.
                If it's a tuple, each item can be either an argument as a string, or a 2-tuple key/value pair.

        Returns: str.
            The query string in the form "key1&key2=value2&key3=value3"
        """

        if type(query) is str: return query

        queryList = []

        for arg in query:
            if type(arg) is str:
                if arg:
                    queryList.append(arg)
            else:
                queryList.append( "=".join(arg) )

        return "&".join(queryList)

    def __post(self, query, bufsize = 0):
        """Posts a query and returns a dict corresponding to the json reply
        
        Args:
            query: tuple.
                The list of arguments, which are themselves 2-tuples of key-value pairs (value may be an empty string)
            bufsize: int.
                The maximum amount of data to be received at once is specified by bufsize.
                
        Returns: dict or None.
            The Daemon reply converted from json to a python dict.
            None if there is an error or the Daemon is unavailable.
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        query = self.__buildQuery( query )

        log( query, LogLevel.DataSent)

        try: s.connect((self.address, self.port))
        except ConnectionRefusedError:
            log("Daemon can't be reached", LogLevel.Debug)
            return
        except Exception as e:
            log("Daemon can't be reached", LogLevel.Debug)
            log("Error: " + e, LogLevel.Critical)
            return

        s.sendall(query.encode('utf-8'))

        if bufsize == 0:
            s.close()
            return None

        data = s.recv(bufsize)
        s.close()

        try:
            obj = json.loads(data)
        except:
            log("Invalid reply data from the Ramses Daemon.", LogLevel.Critical)
            obj = {
                'accepted': False,
                'success': False
            }
            return obj

        if not obj['accepted']: log("Unknown Ramses Daemon query: " + obj['query'], LogLevel.Critical)
        if not obj['success']: log("Warning: the Ramses Daemon could not reply to the query: " + obj['query'], LogLevel.Critical)       
        if obj['message']: log(obj['message'], LogLevel.Debug)

        return obj

    def __testConnection(self):
        """Checks if the Ramses Daemon is available"""

        data = self.ping()

        if data is None:
            log("Daemon unavailable", LogLevel.Debug)
            return False
  
        content = data['content']
        if content is None:
            log("Daemon did not reply correctly")
            return False
        if content['ramses'] == "Ramses": return True

        log("Invalid content in the Daemon reply", LogLevel.Critical)
        return False

    def __checkUser(self):
        data = self.__post('ping')
        if data is None: return False
        content = data['content']
        if content is None: return False
        try:
            ok = content['logged-in']
        except KeyError:
            return False
        return ok

    def __noUserReply(self, query):
        log( Log.NoUser, LogLevel.Debug)
        return {
            'accepted': False,
            'success': False,
            'message': Log.NoUser,
            'query': query,
            'content': None
        }

    def ping(self):
        """Gets the version and current user of the ramses daemon.

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.

        Returns: dict.
            Read http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        """
        return self.__post('ping', 1024)

    def raiseWindow(self):
        """Raises the Ramses Client application main window.
        
        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        """
        self.__post('raise')

    def getAssets(self):
        """Gets the list of the assets for the current project

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getAssets')
        return self.__post( "getAssets", 1048576 )

    def getCurrentProject(self):
        """Gets the current project

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getCurrentProject')
        return self.__post( "getCurrentProject", 1024 )

    def getPipes(self):
        """Gets the list of the pipes for the current project

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getPipes')
        return self.__post( "getPipes", 1048576 )

    def getProjects(self):
        """Gets the list of the projects

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getProjects')
        return self.__post( "getProjects", 32768 )

    def getShots(self, filter = ""):
        """Gets the list of the shots for the current project

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getShots')
        if filter == "": return self.__post( ("getShots"), 1048576 )
        return self.__post( (
            "getShots",
            ('filter', filter)
            ),
            1048576  )

    def getStates(self):
        """Gets the list of the states

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getStates')
        return self.__post( "getStates", 2048 )

    def getSteps(self):
        """Gets the list of the steps

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getSteps')
        return self.__post( "getSteps", 1048576 )

    def setCurrentProject(self, projectShortName):
        """Sets the current project.

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('setCurrentProject')
        return self.__post( (
            "setCurrentProject",
            ('shortName', projectShortName)
            ) )

    def getCurrentUser(self):
        """Gets the current user

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: dict.
        """

        if not self.__checkUser(): return self.__noUserReply('getCurrentUser')
        return self.__post( "getCurrentUser", 1024 )

    def getAssetGroups(self):
        """Gets the asset group list

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: list
        """

        if not self.__checkUser(): return self.__noUserReply('getAssetGroups')
        return self.__post( "getAssetGroups", 2048 )

    def getCurrentStatus(self, itemShortName, itemName, itemType='SHOT'):
        """Gets the current status (list) of an item

        Read the Ramses Daemon reference at http://ramses-docs.rainboxlab.org/dev/daemon-reference/ for more information.
        
        Returns: list
        """
        return self.__post( (
            "getCurrentStatus",
            ('shortName', itemShortName),
            ('name', itemName),
            ('type', itemType)
            ), 8192 )

# used for testing
if __name__ == "__main__":
    daemon = RamDaemonInterface()
    print ( daemon.getCurrentStatus("SEA", "Sea", "ASSET") )
