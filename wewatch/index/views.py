#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from wechat import wechatSession

WcSession = wechatSession()

def login(request):
    if request.method == 'GET':
        url = WcSession.get_QRImage_url()
        uuid = WcSession.get_uuid()
        return render(request, 'login.html',{'state':0,'url':url,'uuid':uuid}) #login page
    elif request.method == 'POST':      
        state =  request.POST.get("state", None)
        if not WcSession._check_QRImag_Validation():
            url = WcSession.get_QRImage_url()
            uuid = WcSession.get_uuid()
            return HttpResponse('???')
        else:
            print('2')
            if WcSession.login():
                print('3')
                WcSession.webwxinit()
                return HttpResponseRedirect('user')

def check_login(request):
    if request.method == 'GET':
        while 1:
            status = WcSession.check_login()
            if status == '200':
                #log in
                return HttpResponseRedirect('user')
            elif status == '201':
                # need comfirm at mobile
                return HttpResponse({'status':'Please press confirm on your mobilephone'})
            elif status == '408':
                WcSession.refresh_uuid()
                return HttpResponseRedirect('')
            else:
                WcSession.refresh_uuid()
                return HttpResponseRedirect('')


