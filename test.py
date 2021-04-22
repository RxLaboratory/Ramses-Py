from ramses import Ramses

# TEST Daemon Interface
ramses = Ramses.instance
di = ramses.daemonInterface()
print( di.getCurrentProject() )
print( di.getPipes() )