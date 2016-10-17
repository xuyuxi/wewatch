from django.shortcuts import render
from core.wechat import wechatSession
import time, requests
import re
WcSession = wechatSession()
def login(request):
    url = WcSession.get_QRImage_url()
    uuid = WcSession.get_uuid()
    return render(request, 'login.html',{'url':url,'uuid':uuid}) #login page
