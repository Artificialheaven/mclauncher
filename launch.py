import json
import os.path

from launcher import LauncherEvent


def start(game_version, name='Steve', game_dir='.minecraft', java_path=None, online=False):
    # java path = 'F:/JDK/17e/bin/java.exe'
    launcher = LauncherEvent.Launcher(game_version, game_dir, java_path)
    launcher.options.clear()
    launcher.options['username'] = name

    if online:
        with open('./data/login.json', 'r', encoding='utf-8') as f:
            import json
            js = json.load(f)
            for i in js['item']:
                if i['name'] == name:
                    launcher.UUID = i['uuid']
                    launcher.ACCESSTOKEN = i['access_token']
                    break

    launcher.start_game()


def get_version_list(game_dir='.minecraft'):
    def research_dir(path):
        files = os.listdir(path)
        dirs = []
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                dirs.append(file_path)
        return dirs

    try:
        dirs = research_dir(game_dir + '/versions/')
        if len(dirs) > 0:
            for i in range(len(dirs)):
                dirs[i] = dirs[i].split('/')[2]

        return dirs
    except FileNotFoundError:
        os.mkdir('./.minecraft/')
        os.mkdir('./.minecraft/versions')
        return []


def can_use_jre8(version):
    _version =version.split('.')
    if int(_version[1]) > 16:
        return False
    return True


def get_all_user():
    with open('./data/login.json', 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
        if content == '':
            return []
        js = json.loads(content)
        items = js['item']
        li = []
        for i in items:
            li.append(i['name'])
        return li
