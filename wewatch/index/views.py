from django.shortcuts import render
import time, requests
import re

def login(request):
    session = requests.Session()
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
        'fun': 'new',
        'lang': 'en_US',
        '_': int(time.time()),
        }
    r = session.get(url, params = params)
    
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
    data = re.search(regx, r.text)
    if data and data.group(1) == '200': 
        uuid = data.group(2)
        url = 'https://login.weixin.qq.com/qrcode/' + uuid
	return render(request, 'login.html',{'url':url}) #login page
