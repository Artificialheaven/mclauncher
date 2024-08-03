import time

import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By


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

token = ms.lstrip('https://login.live.com/oauth20_desktop.srf?code=').rstrip('&lc=2052')
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
print('access_token: ', at)
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

print('user name: ', _mc['username'])
print('access token: ', _mc['access_token'])

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
print('skin: ')
print('    id: ' + uid['skins'][0]['id'])
print('    url: ' + uid['skins'][0]['url'])
print('capes: # 披风')
print('    id: ' + uid['capes'][0]['id'])
print('    url: ' + uid['capes'][0]['url'])
print('    alias: ' + uid['capes'][0]['alias'])

with open('./data/skin.png', 'wb') as f:
    f.write(requests.get(uid['skins'][0]['url']).content)

with open('./data/cape.png', 'wb') as f:
    f.write(requests.get(uid['capes'][0]['url']).content)

login_json = {
    'username': uid['name'],
    'uuid': uid['id'],

}
