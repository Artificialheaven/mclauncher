import os
import time

import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By


def login(username: str=None):
    user_refresh_token = ''
    using_refresh_token = False

    if username is not None:
        with open('./data/login.json', 'r', encoding='utf-8') as f:
            js = json.load(f)
            user_list = js['item']
            for i in user_list:
                if i['name'] == username:
                    user_refresh_token = i['refresh_token']
                    using_refresh_token = True
                    break

    if not using_refresh_token:
        # Microsoft Oauth 流程
        driver = webdriver.Chrome()
        uri = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=00000000402b5328&response_type=code&redirect_uri=https:%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_mode=query&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL'
        print(driver.get(uri))
        phone = driver.find_element(by=By.XPATH, value='//input[@type="email"]')
        phone.send_keys('+86')
        while 'https://login.live.com/oauth20_desktop.srf?code=' not in driver.current_url:
            time.sleep(1)
            print(driver.current_url)
        ms = driver.current_url
        print(driver.current_url)
        # token is 授权码
        token = ms.replace('https://login.live.com/oauth20_desktop.srf?code=', '').replace('&lc=2052', '')

        # 授权码获取授权令牌
        url = 'https://login.live.com/oauth20_token.srf'
        mtd = {
                'client_id': '00000000402b5328',
                'code': token,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
                'scope': 'service::user.auth.xboxlive.com::MBI_SSL'
            }
        print('Microsoft token: ', token)
        print('data: ', mtd)
        ret = requests.post(
            url,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=mtd
        )
        js = json.loads(ret.text)
        print(js)
        at = js['access_token']
        refresh_token = js['refresh_token']
        print('refresh_token: ' + refresh_token)
        print('access_token: ', at)
    else:
        # 通过 refresh_token 获取 授权令牌
        url = 'https://login.live.com/oauth20_token.srf'
        mtd = {
            'client_id': '00000000402b5328',
            'refresh_token': user_refresh_token,
            'grant_type': 'refresh_token',
            'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
            'scope': 'service::user.auth.xboxlive.com::MBI_SSL'
        }
        print('refresh token: ', user_refresh_token)
        print('data: ', mtd)
        ret = requests.post(
            url,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=mtd
        )
        js = json.loads(ret.text)
        print(js)
        at = js['access_token']
        refresh_token = js['refresh_token']
        print('refresh_token: ' + refresh_token)
        print('access_token: ', at)


    # Xbox live
    _js = {
       "Properties": {
           "AuthMethod": "RPS",
           "SiteName": "user.auth.xboxlive.com",
           "RpsTicket": at
       },
       "RelyingParty": "http://auth.xboxlive.com",
       "TokenType": "JWT"
    }
    _ret = requests.post(
        'https://user.auth.xboxlive.com/user/authenticate',
        headers={
            'Content-Type': 'application/json',
        },
        json=_js
    )
    print(_ret.text)
    __js = json.loads(_ret.text)
    _token = __js['Token']

    # XSTS
    datas = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                _token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }
    xsts = requests.post(
        'https://xsts.auth.xboxlive.com/xsts/authorize',
        headers={
            'Content-Type': 'application/json',
        },
        json=datas
    )
    xsts_js = json.loads(xsts.text)
    xsts_token = xsts_js['Token']
    uhs = xsts_js['DisplayClaims']['xui'][0]['uhs']

    # Minecraft access token get
    minecraft_token = {
        "identityToken": f"XBL3.0 x={uhs};{xsts_token}"
    }
    print('Minecraft_token: ')
    print(minecraft_token)
    _mc_at = requests.post(
        'https://api.minecraftservices.com/authentication/login_with_xbox',
        headers={
            'Content-Type': 'application/json',
        },
        json=minecraft_token
    )
    print(_mc_at.text)
    _mc = json.loads(_mc_at.text)
    minecraft_access_token = _mc['access_token']    # access token 启动游戏用
    print('user name: ', _mc['username'])
    print('access token: ', _mc['access_token'])

    # 是否拥有游戏
    store = requests.get(
        'https://api.minecraftservices.com/entitlements/mcstore',
        headers={
            'Authorization': 'Bearer ' + _mc['access_token']
        }
    )
    print(store.text)
    items = json.loads(store.text)
    game_list = []
    for i in items['items']:
        game_list.append(i['name'])

    # 获取 uuid
    _uuid = requests.get(
        'https://api.minecraftservices.com/minecraft/profile',
        headers={
            'Authorization': 'Bearer ' + _mc['access_token']
        }
    )
    print(_uuid.text)

    # 汇总全部登陆数据

    uid = json.loads(_uuid.text)
    print('=====================')
    print('game list: ', game_list)

    print('username: ' + uid['name'])
    print('uuid: ' + uid['id'])
    print('access_token:  ' + minecraft_access_token)
    print('skin: ')
    print('    id: ' + uid['skins'][0]['id'])
    print('    url: ' + uid['skins'][0]['url'])
    print('capes: # 披风')
    print('    id: ' + uid['capes'][0]['id'])
    print('    url: ' + uid['capes'][0]['url'])
    print('    alias: ' + uid['capes'][0]['alias'])
    name = uid['name']
    uuid = uid['id']

    if not os.path.exists(f'./data/{name}'):
        os.mkdir(f'./data/{name}')

    with open(f'./data/{name}/skin.png', 'wb') as f:
        f.write(requests.get(uid['skins'][0]['url']).content)

    with open(f'./data/{name}/cape.png', 'wb') as f:
        f.write(requests.get(uid['capes'][0]['url']).content)

    if os.path.exists('./data/login.json'):
        t = 'r+'
    else:
        t = 'w'

    with open('./data/login.json', 'w+', encoding='utf-8') as f:
        if f.read() == '':
            login_json = {
                'item': [{
                    'name': name,
                    'uuid': uuid,
                    'access_token': minecraft_access_token,
                    'refresh_token': refresh_token,
                    'time_stamp': int(time.time())
                }]
            }
            f.write(json.dumps(login_json))
        else:
            _login_json = json.load(f)

            i = 0
            for i in range(len(_login_json['item'])):
                if _login_json['item'][i]['name'] == name:
                    in_lst = True
                    break

            if in_lst:
                _login_json['item'][i] = {
                    'name': name,
                    'uuid': uuid,
                    'access_token': minecraft_access_token,
                    'refresh_token': refresh_token,
                    'time_stamp': int(time.time())
                }
            else:
                _login_json['item'].append(
                    {
                        'name': name,
                        'uuid': uuid,
                        'access_token': minecraft_access_token,
                        'refresh_token': refresh_token,
                        'time_stamp': int(time.time())
                    }
                )
            f.write(json.dumps(_login_json))

    return name, uuid

