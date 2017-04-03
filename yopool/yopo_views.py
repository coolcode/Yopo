from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
import json
from bson import json_util

from .utils import utils
from .repos import repos

repo = repos()


@login_required
def index(request):
    username = request.user.get_username()
    pre = repo.find_preference(username)
    sex = pre["sex"] if pre is not None else 'f'
    p = {"sex": sex}

    users = repo.query_accounts(username, p)

    if len(users)==0:
        return  HttpResponseRedirect('/no_content')

    context = {
        'users': users,
    }

    return render(request, 'yopool/index.html', context)


@login_required
def match(request):
    username = request.user.get_username()
    picid = repo.find_pic_id(username)

    liked_user = request.GET.get("liked_user", '')
    liked_user_model =repo.find_account(liked_user)
    liked_picid = liked_user_model['picid'] #request.GET.get("liked_picid", '')
    context = {
        'liked_user':liked_user,
        'liked_picid': liked_picid,
        'picid': picid,
        'liked_user_display_name': liked_user_model['display_name'],
    }
    return render(request, 'yopool/match.html', context)


@login_required
@requires_csrf_token
def like(request):
    username = request.user.get_username()
    data = utils.parse_json(request)
    liked_user = data['liked_user']
    repo.save_like_result(username, liked_user)
    status = repo.is_liked(liked_user, username)

    #This is a trick! if you like bruce, bruce likes you too. :)
    if(liked_user=='bruce'):
        status = 'yes'

    #match!
    if status=='yes':
        repo.save_match_result(username, liked_user)
        repo.send_msg(liked_user, username, 'Hello! ☺ ')

    context = {'status': status, "msg": '%s likes %s' %(username, liked_user)}

    return HttpResponse(json.dumps(context), content_type='application/json')


@login_required
@requires_csrf_token
def dislike(request):
    username = request.user.get_username()
    data = utils.parse_json(request)
    disliked_user = data['disliked_user']
    repo.save_dislike_result(username, disliked_user)

    context = {'status': 'no', "msg": '%s dislikes %s' %(username, disliked_user)}

    return HttpResponse(json.dumps(context), content_type='application/json')


@login_required
def no_content(request):
    context = {}
    return render(request, 'yopool/no_content.html', context)


@login_required
def message(request):
    username = request.user.get_username()

    users = repo.find_match_list(username)
    context = {
        'users': users,
    }

    return render(request, 'yopool/message.html', context)

@login_required
def chat(request):
    username = request.user.get_username()
    chat_username = request.GET.get('user','')
    chat_user = repo.find_account(chat_username)
    current_user = repo.find_account(username)
    msg_list = repo.find_msg(username, chat_username)

    context = {
        'chat_user': chat_user,
        'current_user': current_user,
        'msg_list': msg_list
    }

    return render(request, 'yopool/chat.html', context)


@login_required
@requires_csrf_token
def send_msg(request):
    current_user = request.user.get_username()
    data = utils.parse_json(request)
    chat_user = data['chat_user']
    msg = data['msg']
    repo.send_msg(current_user, chat_user, msg)

    context = {'status': 'ok'}

    return HttpResponse(json.dumps(context), content_type='application/json')


@login_required
@requires_csrf_token
def query_msg(request):
    current_user = request.user.get_username()
    data = utils.parse_json(request)
    chat_user = data['chat_user']
    msg_list = repo.find_msg(current_user, chat_user)
    context = {'msg_list': msg_list}

    return HttpResponse(json.dumps(context, default=json_util.default), content_type='application/json')



def demo(request):
    context = {}
    return render(request, 'common/demo.html', context)