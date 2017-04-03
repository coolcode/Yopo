from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import cloudinary
import cloudinary.uploader
import cloudinary.api
import datetime
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .repos import repos
repo = repos()


@requires_csrf_token
def register(request):

    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        context = dict(username=username, password=password, error='')
        try:
            user = User.objects.create_user(username, '%s@yopo.com' % username,  password)
            login(request, user)
            muser = dict(name=username,
                        display_name=username,
                        password=password,
                        birthday=datetime.datetime(1997, 1, 1),
                        sex="m",
                        memo="",
                        picid='v1476794414/empty',
                        create_date=datetime.datetime.utcnow())
            repo.save_account(muser)

            return HttpResponseRedirect('/info')

        except Exception as e:
            context["error"] = "Error: %s" % str(e)

    return render(request, 'accounts/register.html', context)

@requires_csrf_token
def login_view(request):
    next = request.GET.get('next', '/')
    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        context = dict(username=username, password=password, error='')
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                # A backend authenticated the credentials
                # save user on session
                login(request, user)

                return HttpResponseRedirect(next)

            else:
                # No backend authenticated the credentials
                context["error"] = "Please check your user name or password."

        except Exception as e:
            context["error"] = "Error: %s" % str(e)

    return render(request, 'accounts/login.html', context)


@login_required
@requires_csrf_token
def info(request):
    username = request.user.get_username()
    user = repo.find_account(username)

    if request.method == 'POST':
        user['display_name'] = request.POST['display_name']
        user['sex'] = ('m' if request.POST['sex'] == 'Male' else 'f')
        user['memo'] = request.POST['memo']
        user['update_date'] = datetime.datetime.utcnow()
        repo.save_account(user)

        user_pre = repo.find_preference(username)
        if user_pre is None:
            user_pre = dict(user=username,
                            sex='f',
                            age_from=18,
                            age_to=30,
                            create_date=datetime.datetime.utcnow()
                            )
        user_pre['sex'] = ('m' if user['sex']=='f' else 'f')
        repo.save_preference(user_pre)

    return render(request, 'accounts/info.html', user)

@login_required
@requires_csrf_token
def preference(request):
    username = request.user.get_username()

    if request.method == 'POST':
        user_pre = dict(user=username,
                        sex=('m' if request.POST['sex']=='Male' else 'f'),
                        age_from=int(request.POST['age_from']),
                        age_to=int(request.POST['age_to']),
                        create_date=datetime.datetime.utcnow()
                        )
        repo.save_preference(user_pre)

    user_pre = repo.find_preference(username)

    if(user_pre is None):
        user_pre = dict(user=username,
                        sex='f',
                        age_from=18,
                        age_to=30,
                        create_date=datetime.datetime.utcnow()
                        )
        repo.save_preference(user_pre)

    user_pre['sex_full_name'] = 'Male' if user_pre['sex']=='f' else 'Female'
    context = dict(user_pre=user_pre, username=username)

    return render(request, 'accounts/preference.html', context)


@login_required
@requires_csrf_token
def upload_photo(request):
    username = request.user.get_username()

    user_img = repo.find_pic_id(username)
    context = dict(username=username, user_img=user_img)

    if request.method == 'POST':
        files = request.FILES.getlist('image')
        for f in files:
            r = cloudinary.uploader.upload(f, public_id=("u/%s"%username))
            url = r["url"]
            picid = url.replace("http://res.cloudinary.com/yopo/image/upload/", "")
            picid = picid[0:len(picid)-4]
            account_img = dict(url=url,
                               picid=picid,
                               user=username,
                               tag="main",
                               create_date=datetime.datetime.utcnow())
            repo.save_account_pics(account_img)
            context = dict(user_img=picid, username=username)

        return HttpResponseRedirect('/info')

    return render(request, 'accounts/upload_photo.html', context)


@login_required
@requires_csrf_token
def change_password(request):

    username = request.user.get_username()
    context = dict(old_password='', error='')

    if request.method == 'POST':
        old_password = request.POST['old_password']

        context = dict(old_password=old_password, error='')

        try:
            user = authenticate(username=username, password=old_password)
            if user is not None:
                new_password = request.POST['new_password']
                u = User.objects.get(username=username)
                u.set_password(new_password)
                u.save()

                user = authenticate(username=username, password=new_password)
                login(request, user)

                return HttpResponseRedirect('/info')

            else:
                # No backend authenticated the credentials
                context["error"] = "Please check your password."

        except Exception as e:
            context["error"] = "Error: %s" % str(e)

    return render(request, 'accounts/change_password.html', context)


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required
def delete_account(request):
    username = request.user.get_username()
    u = User.objects.get(username=username)
    u.delete()
    repo.delete_account(username)

    return HttpResponseRedirect('/login')


def init_old(request):
    users = User.objects.all()
    result = []
    for user in users:
        try:
            repo.find_account(user.username)
            name =  user.username
            user.delete()
            result.append("deleted user: %s " % (name))
        except Exception as e:
            result.append("Error: %s" % str(e))
    text = '<br>'.join(result)

    return HttpResponse(text)


def init2(request):
    users = repo.find_all_accounts()
    result = []
    for user in users:
        try:
            username = user['name']
            password = user['password']
            u = User.objects.create_user(username, '%s@yopo.com' % username, password)
            result.append("Created user: %s (%s)" % (user['name'], user['display_name']))
        except Exception as e:
            result.append("Error: %s" % str(e))
    text = '<br>'.join(result)

    return HttpResponse(text)


def init(request):
    repo.clear_preference()
    result = ['ok']
    text = '<br>'.join(result)

    return HttpResponse(text)


def test(request):
    return HttpResponse("OK: %s" % "test")

