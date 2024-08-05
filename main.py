import os.path

import login
from launch import start, get_version_list, get_all_user
from downloader.version_manifest import VersionManifest
from downloader.JavaClient import DownloadClinet

from tkinter import *

from ui import MainUI


def eoc(file):
    if not os.path.exists(file):
        os.mkdir(file)


file_list = [
    './.minecraft/', './.minecraft/versions/', './data'
]
for i in file_list:
    eoc(i)


version_manifest = VersionManifest()
print(version_manifest.get_versions(only_release=True))


main_ui = MainUI()
