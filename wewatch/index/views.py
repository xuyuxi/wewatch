#coding=utf-8
from django.shortcuts import render
import requests
import ssl
import re
import os
import time

DEBUG = False


class wechatSession(object):
    '''
    class wechatSession
    '''
    MAX_GROUP_NUM = 2
    INTERFACE_CALLING_INTERVAL = 50
    MAX_PROGRESS_LEN = 50
    
    def __init__(self,):
        self.uuid = ''
        self.wxsid = ''
        self.wxuin = ''
        self.myRequests = requests.Session()
        if hasattr(ssl, '_create_unverified_context'): 
            ssl._create_default_https_context = ssl._create_unverified_context
        headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
        self.myRequests.headers.update(headers)
    def _get_uuid(self,):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
                'appid': 'wx782c26e4c19acffb',
                'fun': 'new',
                'lang': 'zh_CN',
                '_': int(time.time()),
            }
        r = self.myRequests.get(url=url, params=params)
        r.encoding = 'utf-8'
        data = r.text

        # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, data)
    
        code = pm.group(1)
        self.uuid = pm.group(2)
    
        if code == '200':
            return True
    
        return False
    def get_QRImage_url(self,):
        if self.uuid == '':
            self._get_uuid()
        return  'https://login.weixin.qq.com/qrcode/' + self.uuid
    def get_uuid(self,):
        if self.uuid == '':
            self._get_uuid()
        return  self.uuid

WcSession = wechatSession()

def login(request):
    if request.method == 'GET':
        url = WcSession.get_QRImage_url()
        uuid = WcSession.get_uuid()
        return render(request, 'login.html',{'url':url,'uuid':uuid}) #login page
    elif request.method == 'POST':
        request['uudi'] = uuid
        print(uuid)