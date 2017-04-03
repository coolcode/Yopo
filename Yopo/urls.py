"""Yopo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from yopool import account_views, yopo_views

urlpatterns = [
    #url(r'^admin', admin.site.urls),
    url(r'^login', account_views.login_view, name='login'),
    url(r'^register', account_views.register, name='register'),
    url(r'^change_password', account_views.change_password, name='change_password'),
    url(r'^pre', account_views.preference, name='preference'),
    url(r'^info', account_views.info, name='info'),
    url(r'^upload_photo', account_views.upload_photo, name="upload_photo"),
    url(r'^logout', account_views.logout_view, name="logout_view"),
    url(r'^delete_account', account_views.delete_account, name="delete_account"),
    url(r'^init', account_views.init, name="init"),
    url(r'^$', yopo_views.index, name="index"),
    url(r'^match', yopo_views.match, name="match"),
    url(r'^like', yopo_views.like, name="like"),
    url(r'^dislike', yopo_views.dislike, name="dislike"),
    url(r'^no_content', yopo_views.no_content, name="no_content"),
    url(r'^message', yopo_views.message, name="message"),
    url(r'^chat', yopo_views.chat, name="chat"),
    url(r'^send_msg', yopo_views.send_msg, name="send_msg"),
    url(r'^query_msg', yopo_views.query_msg, name="query_msg"),
    url(r'^demo', yopo_views.demo, name="demo"),

]