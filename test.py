from ramses import *


# TEST Daemon Interface
ramses = Ramses.instance
di = ramses.daemonInterface()
print( di.getCurrentProject() )