from time import perf_counter
from ramses import (
    log,
    LogLevel,
    RamSettings,
    RamObject,
    RamState,
    RamFileType,
    RamUser,
    RamItem,
    RamMetaDataManager,
    Ramses
    )

settings = RamSettings.instance()
settings.logLevel = LogLevel.Debug

ramses = Ramses.instance()

# daemon = RamDaemonInterface.instance()

testPaths = (
    'C:/Users/Duduf/Ramses/Projects/FPE/02-PROD/FPE_G_MOD',
    'C:/TEMP/MAYA/MAYA_G_Tests.mb',
    'C:/Users/Duduf/Ramses/Projects/FPE/05-SHOTS/FPE_S_001',
    'C:/Users/Duduf/Ramses/Projects/FPE/04-ASSETS/Characters/FPE_A_TRISTAN/FPE_A_TRISTAN_MOD',
    'C:/Users/Duduf/Ramses/Projects/FPE/02-PROD/FPE_G_ANIM/FPE_G_ANIM_Templates/FPE_G_ANIM_Template.mb'
)

def ram():
    projects = Ramses.instance().projects()
    for p in projects:
        print( p )
        for step in p.steps():
            print( step )

def ramObjects():
    o = RamObject("Object Name", "OSN")
    log( o, LogLevel.Debug )
    log( RamObject.getObjectShortName(o), LogLevel.Debug )
    log( RamObject.getObjectShortName("SN"), LogLevel.Debug )
    d = { 'name': "Dict Object", 'shortName': "DO" }
    o = RamObject.fromDict( d )
    log( o, LogLevel.Debug )

def ramStates():
    s = RamState( "Test", "T", 50, [255,0,0] )
    log (s, LogLevel.Debug)

def ramFileTypes():
    ft = RamFileType("Jpeg", "jpg", ('.jpg', '.jpeg'))
    log( ft )

def ramUsers():
    u = RamUser.fromDict( {
        'name': "Nico Duf",
        'shortName': "Duduf",
        'folderPath': 'C:/Users/Duduf/Ramses/Users/Duduf',
        'role': 'ADMIN'
    })
    log( u )
    log( u.configPath() )

def ramItem():
    item = RamItem.fromPath(testPaths[1])
    print(item)
    if item:
        print(item.stepFolderPath("Tests"))
        print(item.currentStatus("Tests"))
        print(item.itemType())
        print(item.stepFolderPath("Tests"))
        print(item.currentStatus())
        print(item.latestVersionFilePath())
        print(item.versionFolderPath("Tests"))
    item = RamItem.fromPath(testPaths[2])
    print(item)
    if item:
        print(item.stepFilePaths("ANIM"))
        print(item.versionFilePaths("", "ANIM"))
    item = RamItem.fromPath(testPaths[3])
    print(item)
    if item:
        print(item.stepFolderPath("RIG"))
        print(item.stepFilePaths("RIG"))
        print(item.versionFilePaths("", "RIG"))
    item = RamItem.fromPath(testPaths[4])
    print(item)
    if item:
        print(item.itemType())
        print(item.currentStatus())
        print(item.latestVersionFilePath())
        print(item.versionFolderPath())
        print(item.versionFilePaths())

def metadata():
    RamMetaDataManager.setComment(testPaths[1], "Test comment")
    print( RamMetaDataManager.getComment( testPaths[1] ) )

def project():
    project = ramses.project("FPE")
    print(project)
    shots = project.shots()
    for shot in shots:
        print( shot )

def perfTests():
    project = ramses.project("FPE")

    for i in range (0,20):
        tic = perf_counter()
        steps = project.steps()
        print(steps)
        toc = perf_counter()

        print('Iteration ' + str(i) + ' took ' + str(int(toc-tic)) + ' s.')



# === TESTS ===

# ramObjects()
# ramStates()
# ramFileTypes()
# ramUsers()
# ram()
ramItem()
# metadata()
# project()
# perfTests()
