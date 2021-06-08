# from time import perf_counter
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
    RamFileManager,
    Ramses,
    RamStep
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
    'C:/Users/Duduf/Ramses/Projects/FPE/02-PROD/FPE_G_ANIM/FPE_G_ANIM_Templates/FPE_G_ANIM_Template.mb',
    'D:/SWAP/TEMP/testfile_G_bis.mb',
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

def ramItem(pathIndex, step=''):
    item = RamItem.fromPath(testPaths[pathIndex])
    print(item)
    if item:
        print(item.stepFolderPath(step))
        print(item.stepFilePaths(step))
        print(item.currentStatus(step))
        print(item.itemType())
        print(item.stepFolderPath(step))
        print(item.currentStatus())
        print(item.latestVersionFilePath())
        print(item.versionFolderPath(step))
        print(item.projectShortName())

def metadata():
    RamMetaDataManager.setComment(testPaths[1], "Test comment")
    print( RamMetaDataManager.getComment( testPaths[1] ) )

def project():
    project = ramses.project("FPE")
    print(project)
    shots = project.shots()
    for shot in shots:
        print( shot )

    pipes = project.pipes()
    for pipe in pipes:
        for pipeFile in pipe.pipeFiles():
            print( pipeFile )

    print( project.assetGroups() )
    for asset in project.assets( "Characters" ):
        print( asset )
        print( asset.itemType() )
        print( asset.group() )

def perfTest( method, numIterations=20 ):
    print('=== Perf Test Begin ===')
    start = perf_counter()
    prevIt = 0.0
    firstIt = 100000.0
    for i in range (0,numIterations):
        tic = perf_counter()
        method()
        toc = perf_counter()
        it = toc-tic
        dif = it - prevIt
        prevIt = it
        if i == 0:
            firstIt = it
        if it < 0.001:
            print(' > Iteration ' + str(i) + ' is too fast to be measured.')
            continue
        # Round
        it = int(it*1000)/1000.0
        dif = int( (dif / it)*1000 ) / 10.0
        print(' > Iteration ' + str(i) + ' took ' + str(it) + 's. (variation: ' + str(dif) + ' %)')
    end = perf_counter()
    print('=== Total Time: ' + str(int(end-start)) + ' s.' + " ===")
    if firstIt > 0.001:
        endDif = prevIt - firstIt
        endDifP = int( (endDif / firstIt)*1000 ) / 10.0
        print('=== Total Variation: ' + str(endDifP) + ' %.' + " ===")



# === TESTS ===

# ramObjects()
# ramStates()
# ramFileTypes()
# ramUsers()
# ram()
# ramItem(5)
# metadata()
project()


