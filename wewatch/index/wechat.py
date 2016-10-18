import requests
import ssl
import re
import os
import threading
import time
import xml.dom.minidom
def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if DEBUG or Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True

class wechatSession(object):
    '''
    class wechatSession
    '''
    MAX_GROUP_NUM = 2
    INTERFACE_CALLING_INTERVAL = 50
    MAX_PROGRESS_LEN = 50
    
    def __init__(self,):
        self.myRequests = requests.Session()
        #before login
        self.uuid = ''
        self.flag = 0 # 标示uuid是否可用，1可用，2不可用
        self.deviceId = 'e000000000000000'
        #fetch after login
        self.base_uri = ''
        self.redirect_uri = ''
        self.skey = ''
        self.wxsid = ''
        self.wxuin = ''
        self.pass_ticket = ''
        #user info
        self.ContactList = []
        self.My = []
        self.SyncKey = []

        
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
            self.flag = 1
            return True
    
        return False
    def _check_QRImag_Validation(self,):
        
        if self.flag == 0:
            print('flag0')
            self._get_uuid()
            print('getuuid')
        while True:
            url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=1&uuid=%s&_=%s' % (
            self.uuid, int(time.time()))
            r = self.myRequests.get(url=url)
            r.encoding = 'utf-8'
            data = r.text

            # print(data)

            # window.code=500;
            regx = r'window.code=(\d+);'
            pm = re.search(regx, data)

            code = pm.group(1)
            if code == '200':
                time.sleep( 1 )
            elif code == '200':  # 已登录
                self.flag = 0
                regx = r'window.redirect_uri="(\S+?)";'
                pm = re.search(regx, data)
                self.redirect_uri = pm.group(1) + '&fun=new'
                self.base_uri = self.redirect_uri[:self.redirect_uri.rfind('/')]
                # push_uri与base_uri对应关系(排名分先后)(就是这么奇葩..)
                services = [
                    ('wx2.qq.com', 'webpush2.weixin.qq.com'),
                    ('qq.com', 'webpush.weixin.qq.com'),
                    ('web1.wechat.com', 'webpush1.wechat.com'),
                    ('web2.wechat.com', 'webpush2.wechat.com'),
                    ('wechat.com', 'webpush.wechat.com'),
                    ('web1.wechatapp.com', 'webpush1.wechatapp.com'),
                ]
                self.push_uri = base_uri
                for (searchUrl, pushUrl) in services:
                    if self.base_uri.find(searchUrl) >= 0:
                        self.push_uri = 'https://%s/cgi-bin/mmwebwx-bin' % pushUrl
                        break
                return True
            elif code == '408':  # 超时
                self.flag = 0
                return False
            elif code == '400' or code == '500':
                self.flag = 0
                return False
            else:
                self.flag = 0
                return False
    def _heartBeatLoop(self,):
        while True:
            selector = self._syncCheck()
            if selector != '0':
                self._webwxsync()
            time.sleep(1)
    def _syncCheck(self,):
        print('_syncCheck')
        url = self.push_uri + '/synccheck?'
        params = {
            'skey': self.skey,
            'sid': self.sid,
            'uin': self.uin,
            'deviceId': self.deviceId,
            'synckey': self._syncKey(),
            'r': int(time.time()),
        }

        r = self.myRequests.get(url=url,params=params)
        r.encoding = 'utf-8'
        data = r.text

        # print(data)

        # window.synccheck={retcode:"0",selector:"2"}
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, data)

        retcode = pm.group(1)
        selector = pm.group(2)

        return selector


    def _webwxsync():
        BaseRequest = {
            'Uin': int(self.wxuin),
            'Sid': wself.xsid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
        url = self.base_uri + '/webwxsync?lang=zh_CN&skey=%s&sid=%s&pass_ticket=%s' % (
            self.skey, self.sid, quote_plus(self.pass_ticket))
        params = {
            'BaseRequest': BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': ~int(time.time()),
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}

        r = self.myRequests.post(url=url, data=json.dumps(params))
        r.encoding = 'utf-8'
        data = r.json()

        # print(data)

        dic = data
        SyncKey = dic['SyncKey']

        state = responseState('webwxsync', dic['BaseResponse'])
        return state

    def login(self,):
        print('login')
        r = self.myRequests.get(url=self.redirect_uri)
        r.encoding = 'utf-8'
        data = r.text

        # print(data)

        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.wxsid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.wxuin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        # print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid,
        # wxuin, pass_ticket))

        if not all((self.skey, self.wxsid, self.wxuin, self.pass_ticket)):
            return False
        return True

    def webwxinit(self,):
        print('webwxinit')
        BaseRequest = {
            'Uin': int(self.wxuin),
            'Sid': wself.xsid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
        url = (self.base_uri + 
            '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
                self.pass_ticket, self.skey, int(time.time())) )
        params  = {'BaseRequest': BaseRequest }
        headers = {'content-type': 'application/json; charset=UTF-8'}

        r = self.myRequests.post(url=url, data=json.dumps(params),headers=headers)
        r.encoding = 'utf-8'
        data = r.json()

        if DEBUG:
            f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
            f.write(r.content)
            f.close()


        # print(data)
        dic = data
        self.ContactList = dic['ContactList']
        self.My = dic['User']
        self.SyncKey = dic['SyncKey']

        state = responseState('webwxinit', dic['BaseResponse'])

        #print('开启心跳线程')
        threading.Thread(target=self._heartBeatLoop)
        return state


    def get_QRImage_url(self,):
        if self.flag == 0:
            self._get_uuid()
        return  'https://login.weixin.qq.com/qrcode/' + self.uuid
    def get_uuid(self,):
        if self.flag == 0:
            self._get_uuid()
        return  self.uuid
    def get_contact(self,):

        url = (self.base_uri + 
            '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
                self.pass_ticket, self.skey, int(time.time())) )
        headers = {'content-type': 'application/json; charset=UTF-8'}


        r = self.myRequests.post(url=url,headers=headers)
        r.encoding = 'utf-8'
        data = r.json()

        if DEBUG:
            f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
            f.write(r.content)
            f.close()

        # print(data)

        dic = data
        MemberList = dic['MemberList']

        # 倒序遍历,不然删除的时候出问题..
        SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage", "qqsync", "floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp", "blogapp", "facebookapp", "masssendapp",
                        "meishiapp", "feedsapp", "voip", "blogappweixin", "weixin", "brandsessionholder", "weixinreminder", "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts", "notification_messages", "wxitil", "userexperience_alarm"]
        for i in range(len(MemberList) - 1, -1, -1):
            Member = MemberList[i]
            if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                MemberList.remove(Member)
            elif Member['UserName'] in SpecialUsers:  # 特殊账号
                MemberList.remove(Member)
            elif Member['UserName'].find('@@') != -1:  # 群聊
                MemberList.remove(Member)
            elif Member['UserName'] == My['UserName']:  # 自己
                MemberList.remove(Member)

        return MemberList
    def get_uid(self,):
        return self.wxuin


