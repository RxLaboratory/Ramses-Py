import os
import rxbuilder.utils as utils
import rxbuilder.py as py
import shutil
from _config import (
    REPO_PATH,
    BUILD_PATH,
)

VERSION = utils.read_version(REPO_PATH)
MOD_PATH = os.path.join( BUILD_PATH, 'ramses-py' )
SRC_PATH = os.path.join( REPO_PATH, 'ramses' )

def build():
    if not os.path.isdir(MOD_PATH):
        os.makedirs(MOD_PATH)

    py.build_folder(
        SRC_PATH,
        os.path.join( MOD_PATH, 'ramses' )
    )

    # Copy Readme and toml
    shutil.copy(
        os.path.join(REPO_PATH, 'README.md'),
        os.path.join(MOD_PATH, 'README.md')
    )
    toml = os.path.join(MOD_PATH, 'pyproject.toml')
    shutil.copy(
        os.path.join(REPO_PATH, 'pyproject.toml'),
        toml
    )

    # Update metadata
    utils.replace_in_file( {
        '#version#': VERSION,
    }, toml)

    config_file = os.path.join(
        MOD_PATH, 'ramses', 'ram_settings.py'
    )
    utils.replace_in_file( {
        '#version#': VERSION,
    }, config_file)

def zip_module():
    zip_file = os.path.join(
        BUILD_PATH,
        'ramses-py_' + VERSION + '.zip'
    )
    utils.zip_dir(MOD_PATH, zip_file)

if __name__ == '__main__':
    utils.wipe(BUILD_PATH)
    build()
    zip_module()
