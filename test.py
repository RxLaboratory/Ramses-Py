from ramses import RamUser
from ramses import RamItem
from ramses import RamProject
from ramses import RamShot
from ramses import RamState
from ramses import RamFileType
from ramses import Ramses


def testUserClass():
    user = RamUser( "Nicolas Dufresne", "Duduf", "/home/user/duduf/Ramses/Users/Duduf", 'ADMIN' )

    print( user.name() )
    print( user.shortName() )
    print( user.role() )
    print( user.folderPath() )
    print( user.configPath() )
    print( user.configPath( True ) )

def testItemClass():
    item = RamItem( "NameItem", "ShortNameItem", "Folder" )

    print( item.name() )
    print( item.shortName() )
    print( item.folderPath() )
    # print( item.currentStatus( step ) )
    # print( item.latestVersion( step ) )
    # print( item.previewFolderPath( step ) )
    # print( item.previewFilePaths( step ) )
    # print( item.publishedFolderPath( step ) )
    # print( item.publishedFilePaths( step ) )
    # print( item.versionFolderPath( step ) )
    # print( item.versionFilePath( step ) )
    # print( item.wipFolderPath( step ) )
    # print( item.wipFilePath( step ) )
    # print( item.isPublished( step ) )
    # print( item.setStatus( status, step ) )
    # print( item.status( step ) )

def testProjectClass():
    proj = RamProject( "ProjectName", "ProjectShortName", "/home/user/duduf/Ramses/Users/Duduf" )

    print( proj.name() )
    print( proj.shortName() )
    print( proj.folderPath ) 
    # print( proj.absolutePath( relativePath ) )
    print( proj.assets() )
    print( proj.assetGroups() )
    print( proj.shots() )
    print( proj.steps() )

def testShotClass():
    shot = RamShot( "ShotName", "ShotShortName" )

    print( shot.name() )
    print( shot.shortName() )
    # print( shot.duration() )
    print( shot.getFromPath( "/home/user/duduf/Ramses/Users/Duduf" ) )

def testStateClass():
    state = RamState( "Work in progress", "WIP", 50, [255, 0, 0])
    
    print( state.name() )
    print( state.shortName() )
    print( state.completionRatio() )
    print( state.color() )

def testFileType():
    fileType = RamFileType( "NameFichier", "ShortNameFichier", ".txt")

    print( fileType.name() )
    print( fileType.shortName() )
    print( fileType.extensions() )

def testRamsesMethods():
    ramses = Ramses.instance
    # print( ramses.currentUser() )
    # print( ramses.currentStep() )
    # print( ramses.currentProject() )


# testUserClass()
# testItemClass()
# testProjectClass()
# testShotClass()
# testStateClass()
# testFileType()
testRamsesMethods()
