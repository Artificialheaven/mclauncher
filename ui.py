import tkinter
import subprocess
import os

import login
from launcher import LauncherEvent
from launch import get_version_list, get_all_user, start
from downloader.version_manifest import VersionManifest
from downloader.JavaClient import DownloadClinet

from tkinter import *


def get_java_path():
    output = subprocess.check_output(['where', 'java'], stderr=subprocess.DEVNULL)
    java_executable = output.decode().strip()
    java_executable = os.path.dirname(java_executable)
    print(output)
    return os.path.join(java_executable, "java.exe")


class MainUI(Tk):
    def __init__(self):
        super().__init__('')
        version_manifest = VersionManifest()
        self.li = version_manifest.get_versions(only_release=True)
        self.listb = Listbox(self)  # 创建两个列表组件
        for item in list(reversed(self.li)):  # 第一个小部件插入数据
            self.listb.insert(0, item)

        Label(self, text='AllVersions').place(x=0, y=0)
        Button(self, text='Download', command=self.on_download_button).place(x=0, y=208)
        self.listb.place(x=0, y=23)

        self.li2 = get_version_list()
        if len(self.li2) > 0:
            self.version = self.li2[0]
        else:
            self.version = ''
        self.listb2 = Listbox(self)  # 创建两个列表组件
        for item in list(reversed(self.li2)):  # 第一个小部件插入数据
            self.listb2.insert(-1, item)
        Label(self, text='GameVersions').place(x=150, y=0)
        Button(self, text='Start', command=self.on_version_select_button).place(x=150, y=208)
        self.listb2.place(x=150, y=23)

        self.li3 = get_all_user()
        self.listb3 = Listbox(self)  # 创建两个列表组件
        for item in list(reversed(self.li3)):  # 第一个小部件插入数据
            self.listb3.insert(0, item)
        Label(self, text='UserList').place(x=300, y=0)
        Button(self, text='Submit', command=self.on_user_select_button).place(x=300, y=208)
        self.listb3.place(x=300, y=23)

        Button(self, text='Login a new account', command=self.on_login_button).place(x=500, y=10)
        Button(self, text='Refresh a new account', command=self.on_refresh_button).place(x=500, y=45)
        Button(self, text='Login with an aurora account').place(x=500, y=45 + 35)
        self.java_dir = Variable()
        Label(self, text='Java dir').place(x=500, y=45 + 35 + 30)
        Entry(self, textvariable=self.java_dir, width=34).place(x=500, y=45 + 35 + 30 + 25)
        self.java_dir.set(get_java_path())
        Label(self, text='Minecraft > 1.17 using minium Java16').place(x=500, y=45 + 35 + 30 + 25 + 25)
        Label(self, text='Minecraft > 1.18 using minium Java17').place(x=500, y=45 + 35 + 30 + 25 + 25 + 25)
        Label(self, text='Minecraft > 1.20.5 using minium Java21').place(x=500, y=45 + 35 + 30 + 25 + 25 + 25 + 25)

        self.title('Minecraft launcher')
        self.geometry('750x250')
        self.iconphoto(False, tkinter.PhotoImage(file='logo.png'))
        self.mainloop()

    def on_download_button(self):
        on_select = self.listb.curselection()[0]
        print(on_select, self.li[on_select])
        DownloadClinet(self.li[on_select])
        self.destroy()
        self.__init__()

    def on_user_select_button(self):
        on_select = self.listb3.curselection()[0]
        print(on_select, self.li3[on_select])
        self.user_name = self.li3[on_select]

    def on_version_select_button(self):
        on_select = self.listb2.curselection()[0]
        print(on_select, self.li2[on_select])
        version = self.li2[on_select]
        print(self.user_name)
        # java_dir = self.java_dir.get()
        # print(1, java_dir)
        # launcher = LauncherEvent.Launcher(self.version, '.minecraft', 'F:/JDK/21e/bin/java.exe')
        # launcher.java_path = java_dir
        # launcher.options['username'] = self.user_name
        #
        # with open('./data/login.json', 'r', encoding='utf-8') as f:
        #     import json
        #     js = json.load(f)
        #     for i in js['item']:
        #         if i['name'] == self.user_name:
        #             launcher.UUID = i['uuid']
        #             launcher.ACCESSTOKEN = i['access_token']
        #             break
        # launcher.options[java_dir] = ''
        # launcher.start_game()
        # del launcher.options
        start(version, name=self.user_name, online=True, java_path=self.java_dir.get())

    def on_login_button(self):
        login.login()
        self.destroy()
        self.__init__()

    def on_refresh_button(self):
        on_select = self.listb3.curselection()[0]
        print(on_select, self.li3[on_select])
        login.login(self.li3[on_select])
