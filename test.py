from ramses import *

# TEST Daemon Interface

di = Ramses.instance.daemonInterface()

print( di.getCurrentProject() )