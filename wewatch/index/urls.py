# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 01:06:52 2016

@author: bruce
"""

from django.conf.urls import include, url
from index import views

urlpatterns = [
    url(r'^$', views.login,name = 'login'),
    url(r'^check$', views.check_login,name = 'check_login'),
    ]
