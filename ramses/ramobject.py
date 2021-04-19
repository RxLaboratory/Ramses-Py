class RamObject():

    def __init__(self, name, shortName):
        self.__name = name
        self.__shortName = shortName
    
    def name(self):
        """return string"""
        return self.__name

    def shortName(self):
        """return string"""
        return self.__shortName