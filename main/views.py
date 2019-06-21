from django.shortcuts import render

import csv, bisect, json, logging, random
from django.conf import settings
from django.contrib.auth.models import User, Group
# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.http import HttpResponse, Http404

from main import models

logger = logging.getLogger(__name__)
PAGE_SIZE = 10

GROUP_DICT = {'admin': '管理员', 'guest': '访客', 'user': '用户'}

# Create your views here.

from django.http import HttpResponse

# 接口
@login_required
def index(request):
    return render(request, 'main/index.html')


@login_required
def game(request, name='firstGame'):
    return render(request, f'main/game.html', {"game_path": f"main/js/{name}.js"})


@login_required
def choose_room(request):
    userDtb = models.User.objects.raw("select a.id, a.name as room_name, group_concat(c.username) as user_name from main_room a left join main_users b on a.id = b.room_id left join auth_user c on c.id = b.user_id group by a.id")
    context = {}
    context['rooms'] = userDtb
    ranks = models.Rank.objects.raw("select id,name from main_rank")
    context['ranks'] = ranks
    sql = "select a.id,a.name from main_rank a left join main_users b on a.id = b.rank left join auth_user c on c.id = b.user_id where c.id = " + request.user.id.__str__()
    currentRank = models.Rank.objects.raw(sql)
    context['current'] = currentRank
    return render(request, 'main/room.html', context)


@login_required
def room(request):
    r = request.GET['r']
    user_id = request.user.id
    models.Users.objects.filter(user_id=user_id).update(room_id=r)
    userDtb = models.User.objects.raw("select a.id, a.name as room_name, group_concat(c.username) as user_name from main_room a left join main_users b on a.id = b.room_id left join auth_user c on c.id = b.user_id group by a.id")
    return redirect('main:choose-room')

@login_required
def choose_rank(request):
    rank = request.GET['rank']
    user_id = request.user.id
    if user_id == 0:
        user_id = random.randint(1,19)
    models.Users.objects.filter(user_id=user_id).update(rank=rank)
    return redirect('main:choose-room')


@login_required
def parachute(request):
    return 1


@login_required
def move(request):
    return 1


@login_required
def certificate(request):
    return 1


@login_required
def choose_cmd(request):
    if request.POST['vote'] == '1':
        return_dict = {
            'success': 1,
            'need_vote': 0,
            'info': 'choose commander success',
            'candidates': ['junzhou', 'hainan'],
            'commander': request.POST['vote_commander']
        }
    else:
        return_dict = {
            'success': 0,
            'need_vote': 1,
            'info': 'there are 2 soldiers with same level, so we need to vote for commander',
            'candidates': ['junzhou', 'hainan'],
            'commander': ''
        }
    return HttpResponse(json.dumps(return_dict))


@login_required
def open_box(request):
    return 1


@login_required
def init(request):
    return 1


# 自定义方法
def get_return_dict_for_navbar(request):
    return dict(user_name=request.user.get_username(), user_group=GROUP_DICT[request.user.groups.all()[0].name])


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
