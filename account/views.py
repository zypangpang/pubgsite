from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group,Permission
from django.db.models import Q

from main.views import GROUP_DICT,merge_two_dicts,get_return_dict_for_navbar


def user_login(request):
    if request.method == 'GET':
        try:
            next = request.GET['next']
        except:
            next = '/'
        return render(request, 'account/login.html', {'error_message': '', 'next': next})
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.POST['next'])
        else:
            return render(request, 'account/login.html', {'error_message': '登录失败，请重试', 'next': request.POST['next']})


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('account:login'))


SHOW_FIELDS = (('用户编号', '20%'), ('用户名', '40%'), ('用户类别', '40%'))
GROUP_DICT = {'admin': '管理员', 'guest': '访客', 'user': '用户'}


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_manage(request):
    init_group=True
    if Group.objects.get(name='admin') and Group.objects.get(name='user') and Group.objects.get(name='guest'):
        init_group=False
    query_raw_result = User.objects.all()
    query_result = []
    for item in query_raw_result:
        # applicant_str = ';'.join([a.name for a in item.applicants.all()])
        # patent_type=PATENT_TYPE_DICT_REVERSE[item.patent_type]
        if item.groups.all():
            query_result.append([item.id, item.username, GROUP_DICT[item.groups.all()[0].name]])
        else:
            query_result.append([item.id, item.username, '无用户组'])
    return render(request, 'account/useradmin.html', merge_two_dicts({ 'query_result': query_result,
                                                      'init_group':init_group,
                                                      'show_fields': SHOW_FIELDS, },
                                                      get_return_dict_for_navbar(request)))


@login_required
@permission_required('auth.change_user', raise_exception=True)
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usergroup = request.POST['user_group']

        try:
            user = User.objects.create_user(username, '', password)
        except:
            return render(request, 'main/show_message.html', {'message': '添加用户失败，该用户是否已经存在？',
                                                              'user_name': request.user.get_username(),
                                                              'success': 0})

        user.groups.set([Group.objects.get(name=usergroup)])

        return redirect(reverse("account:useradmin"))


@login_required
@permission_required('auth.change_user', raise_exception=True)
def del_user(request):
    username = request.POST['username']
    if username == request.user.get_username():
        return render(request, 'main/show_message.html', {'message': '删除用户失败，不能删除自己',
                                                          'user_name': request.user.get_username(),
                                                          'success': 0})
    try:
        User.objects.get(username=username).delete()
    except:
        return render(request, 'main/show_message.html', {'message': '删除用户失败',
                                                          'user_name': request.user.get_username(),
                                                          'success': 0})
    return redirect(reverse("account:useradmin"))


@login_required
@permission_required('auth.change_user', raise_exception=True)
def init_group(request):
    admingroup, created = Group.objects.get_or_create(name='admin')
    usergroup, created = Group.objects.get_or_create(name='user')
    guestgroup, created = Group.objects.get_or_create(name='guest')
    admin_permissions=Permission.objects.all()
    user_permissions=Permission.objects.filter(
        Q(codename__contains='patent') | Q(codename__contains='note'),
        ~Q(codename__contains='delete'),
        ~Q(codename__contains='change'),
        ~Q(codename='view_private_notes')
    )
    admingroup.permissions.set(admin_permissions)
    usergroup.permissions.set(user_permissions)
    guestgroup.permissions.set([])

    return render(request, 'main/show_message.html', {'message': '用户组初始化成功',
                                                          'user_name': request.user.get_username(),
                                                          'success': 1})
@login_required
@permission_required('auth.change_user', raise_exception=True)
def change_pwd(request):
    username=request.POST['username']
    newpwd=request.POST['password']
    try:
        user=User.objects.get(username=username)
        user.set_password(newpwd)
        user.save()
    except:
        return render(request, 'main/show_message.html', {'message': '修改密码失败',
                                                          'user_name': request.user.get_username(),
                                                          'success':0})

    return render(request, 'main/show_message.html', {'message': '修改密码成功',
                                                      'user_name': request.user.get_username(),
                                                      'success': 1})
@login_required
@permission_required('auth.change_user', raise_exception=True)
def change_group(request):
    username = request.POST['username']
    usergroup = request.POST['user_group']
    user=User.objects.get(username=username)

    try:
        user.groups.set([Group.objects.get(name=usergroup)])
    except:
        return render(request, 'main/show_message.html', {'message': '修改用户组失败，是否已初始化用户组？',
                                                          'user_name': request.user.get_username(),
                                                          'success': 0})

    return redirect(reverse("account:useradmin"))

# Create your views here.
