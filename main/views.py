#-*- coding:utf-8 -*-
import json,random
from django.shortcuts import render

import csv, bisect, json, logging, random
import rsa as yynrsa
from . import rsa_jz as rsa
from django.conf import settings
from django.contrib.auth.models import User, Group
# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.http import HttpResponse, Http404

import json,random
from django.shortcuts import render
from django.contrib.auth.models import User

from . import models, prime, lagrange
from . import initialization

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
def db_init(request):
    models.Users.objects.update(is_commander=0, position_x=-1, position_y=-1,
                                public_key=None, private_key=None, mill_rand=None, mill_prime=None,
                                room_id=1, box_key_x=None, box_key_y=None, certificating_with=-1,
                                opening_box=-1, rsa_n=None, vote_to=-1, rank=-1)
    global_state=models.SystemParam.objects.get(key='global_status')
    global_state.intValue=0
    global_state.save()
    print(global_state)

    models.Box.objects.update(password=None)
    for i in range(5):
        j=i+1
        models.Users.objects.filter(id=j).update(user_name=User.objects.get(id=j).username)

    return redirect('main:choose-room')


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
    return redirect('main:choose-room')

@login_required
def choose_rank(request):
    rank = int(request.GET['rank'])
    user_id = request.user.id
    if rank != -1:
        if rank < 1 or rank > 18:
            rank = random.randint(1, 18)
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
    user_id = request.user.id
    user = models.Users.objects.get(id=user_id)
    all_users = models.Users.objects.filter(group_id=user.group_id)

    global_state=models.SystemParam.objects.get(key='global_status').intValue

    commander=models.SystemParam.objects.get(key='commander').strValue
    if commander:
        info = f'选取指挥官成功，指挥官是{commander}。'
        return_dict = {
                'success': 1,
                'need_vote': 0,
                'info': info,
                'candidates': [],
                'commander': commander
            }
        return HttpResponse(json.dumps(return_dict))

    if global_state==4:
        return_dict = {
                'success': 0,
                'need_vote': 0,
                'info': '正在选取指挥官...',
                'candidates':[],
                'commander': ''
            }
        return HttpResponse(json.dumps(return_dict))

    if global_state == 3:
        if request.POST['vote'] == '1':
            authName = request.POST['vote_commander']
            authVC = User.objects.get(username=authName)
            user.vote_to = authVC.id
            user.save()
        need_vote = 0
        candidates=[]
        info='正在投票选出指挥官中，请耐心等待。'
        okFlag = 1
        cs = []
        if user.vote_to<0:
            need_vote=1
            candidates=models.SystemParam.objects.get(key='candidates').strValue.split(',')
            info = f"{', '.join(candidates)}的军衔并列最高，需要投票选出指挥官。"
            okFlag = 0
        else:
            for u in all_users:
                if u.vote_to <0:
                    okFlag = 0
                    break
                else:
                    cs.append(models.Users.objects.get(id=u.vote_to))

        if okFlag == 0:
            return_dict = {
                'success': 0,
                'need_vote': need_vote,
                'info': info,
                'candidates':candidates ,
                'commander': ''
            }
        else:
            commander = voteLeader(cs,all_users)
            authCom = User.objects.get(id=commander.id)
            info = f'选取指挥官成功，指挥官是{authCom.username}。'

            commander=models.SystemParam.objects.get(key='commander')
            commander.strValue=authCom.username
            commander.save()

            return_dict = {
                'success': 1,
                'need_vote': 0,
                'info': info,
                'candidates': [authCom.username],
                'commander': authCom.username
            }
            initialization.change_system_status(4)
        return HttpResponse(json.dumps(return_dict))

    #print(all_users)
    (tempResult,commander,setP,setQ,setR) = findLeader(all_users)
    #print((tempResult,commander,setP,setQ,setR))
    if tempResult == 0:
        authCom = User.objects.get(id=commander.id)
        info = f'选取指挥官成功，指挥官是{authCom.username}。'

        commander=models.SystemParam.objects.get(key='commander')
        commander.strValue=authCom.username
        commander.save()

        return_dict = {
            'success': 1,
            'need_vote': 0,
            'info': info,
            'candidates': [authCom.username],
            'commander': authCom.username
        }
        initialization.change_system_status(4)
    else:
        can = []
        for u in setQ:
            tempAU = User.objects.get(id=u.id)
            can.append(tempAU.username)
        return_dict = {
            'success': 0,
            'need_vote': 1,
            'info': f"{', '.join(can)}的军衔并列最高，需要投票选出指挥官。",
            'candidates': can,
            'commander': ''
        }
        candidates = models.SystemParam.objects.get(key='candidates')
        candidates.strValue = ','.join(can)
        candidates.save()
        initialization.change_system_status(3)

    return HttpResponse(json.dumps(return_dict))



def init(request):
    '''
    :param player_id: the player_id is expected to be in [0, 4]
    :return:
    '''

    return HttpResponse(initialization.get_all_positions(request.user.id))

def get_cur_state(request):
    username = request.user.get_username()
    user_id = request.user.id
    user = models.Users.objects.get(user_id=user_id)

    user.position_x = request.POST['position_x']
    user.position_y = request.POST['position_y']
    user.save()

    user_list = models.Users.objects.all()
    global_status = models.SystemParam.objects.get(key='global_status')
    other_players = {}
    known_count = 0
    for u in user_list:
        same_group = 0
        if u.user_id == user_id:
            continue
        elif u.group_id == user.group_id:
            same_group = 1
            known_count += 1
        other_players[u.user.get_username()] = {'position': [u.position_x, u.position_y],
                                    'known': same_group}

    if (known_count >= 4) and (global_status.intValue == 1):
        global_status.intValue = 2
        global_status.save()

    can_choose_commander = 0
    if global_status.intValue >=2: #and (user.vote_to <= 0):
        can_choose_commander = 1

    return_dict = {
        'player': username,
        'position': [user.position_x, user.position_y],
        'can_choose_commander': can_choose_commander,
        'otherPlayers': other_players
    }

    if user.certificating_with > 0:
        print(f'auth:{user.certificating_with}')
        c_username = User.objects.get(id=user.certificating_with).get_username()
        return_dict['event'] = {'name': 'auth',
                                'username': c_username,
                                'info': '你正在和' + c_username + '认证。'}
    if user.opening_box > 0:
        return_dict['event'] = {'name': 'open_house',
                                'house_id': user.opening_box,
                                'info': '你正在开启' + str(user.opening_box) + '号房子。'}

    global_status = models.SystemParam.objects.get(key='global_status').intValue
    #TODO: fetch candidates list
    if global_status == 3:
        if user.vote_to <= 0:
            candidates = ['junzhou','hainan']
            return_dict['event'] = {'name': 'vote_commander',
                                    'info': '选举指挥官'}
            # 'candidates': candidates,
    elif global_status == 5:
        return_dict['event'] = {'name': 'game_over',
                                'end': 1,
                                'info': '你进入了房子，找到了大量物资与武器。任务成功。'}
    elif global_status == 6:
        return_dict['event'] = {'name': 'game_over',
                                'end': 0,
                                'info': '你走进房子的那一刻，房子突然爆炸，你们被炸死了。'}

    return HttpResponse(json.dumps(return_dict))


def authenticate(request):
    '''
        certificate_result: 1 success, 0 fail
    '''
    from_id = request.user.id
    user = models.Users.objects.get(user_id=from_id)
    to_username = request.POST['userB_id']

    to_id = User.objects.get(username=to_username).id

    user.certificating_with = to_id
    user.save()

    result = rsa.two_way_certificate(from_id, to_id)
    info = ""
    to_user = models.Users.objects.get(id=to_id)
    show_length = 32
    if result == 1:
        rsa.merge_user_group(from_id, to_id)
        info = f"你成功地认证了{to_username}。\n" \
            f"他的rsa_n是{to_user.rsa_n[0:show_length]}...\n" \
            f"他的公钥是{to_user.public_key[0:show_length]}...\n" \
            f"他的私钥是{to_user.private_key[0:show_length]}..."
    else:
        info = f"你对{to_username}的认证失败了。\n" \
            f"他的rsa_n是{to_user.rsa_n[0:show_length]}...\n" \
            f"他的公钥是{to_user.public_key[0:show_length]}..."
    return_dict = {'success': result,
                   'info': info}

    user.certificating_with = -1
    user.save()
    return HttpResponse(json.dumps(return_dict))

def open_house(request):
    # user_id = request.user.id
    user = models.Users.objects.get(user_id=request.user.id)
    position = (user.position_x, user.position_y)
    box_id = -1

    '''
    house 1: (3-6,22-24)
    house 2: (20-23,4-6)
    '''
    house_range = [[1,8,20,26],[18,25,2,8]]
    for i in range(len(house_range)):
        if house_range[i][0]<=position[0]<=house_range[i][1] and \
                house_range[i][2]<=position[1]<=house_range[i][3]:
            box_id=i

    #for i in range(len(house_range)):
    #    if position in house_range[i]:
    #        box_id = i
    #        break

    if box_id < 0:
        return_dict = {'success': 0,
                       'info': '你并不在任何一个房子的旁边。'}
        return HttpResponse(json.dumps(return_dict))

    user.opening_box = box_id
    user.save()

    user_list = models.Users.objects.all()
    key_list = []
    box = models.Box.objects.get(id=box_id+1)
    for u in user_list:
        if u.group_id == user.group_id:
            if house_range[box_id][0]<=u.position_x<=house_range[box_id][1] and \
                    house_range[box_id][2]<=u.position_y<=house_range[box_id][3]:
                key_list.append((u.box_key_x, u.box_key_y))

    print(key_list)
    solve_result = lagrange.solve_lagrange(key_list, box.least_num)
    result = 0
    info = f"打开失败，这个房子的密码是{box.password}但你们输入的密码是{solve_result}。\n" \
        f"your keys are {', '.join([str(k) for k in key_list])}."
    if solve_result == -1:
        result = 0
        info = f"需要3人才能打开，这里只有{len(key_list)}个自己人。"
    elif solve_result == -2:
        result = 0
        info = f"你们的密钥里出现了相同的x。\n" \
               f"你们的密钥是{', '.join([str(k) for k in key_list])}。"
    elif solve_result == box.password:
        result = 1
        info = f"打开成功，房子的密码是{solve_result}。\n" \
            f"你们的密钥是{', '.join([str(k) for k in key_list])}。"

    return_dict = {'success': result,
                   'info': info}
    user.opening_box = -1
    user.save()
    return HttpResponse(json.dumps(return_dict))

def game_over(request):
    ending = request.POST['ending']
    global_status = models.SystemParam.objects.get(key='global_status')
    if ending == '1':
        global_status.intValue = 5
    elif ending == '0':
        global_status.intValue = 6
    global_status.save()
    return_dict = {'success': 1}
    return HttpResponse(json.dumps(return_dict))

# 自定义方法
def get_return_dict_for_navbar(request):
    return dict(user_name=request.user.get_username(), user_group=GROUP_DICT[request.user.groups.all()[0].name])


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def findLeader(s):
    setP = []
    setQ = []
    setR = []
    n = len(s)
    if n == 1:
        return (0, s[0], setP, setQ, setR)
    print("millionaire begin")
    for x in range(n):
        if x == 0:
            setQ.append(s[0])
            continue

        print("comparing %d of rank %d and %d of rank %d " % (0, s[0].rank, x, s[x].rank))
        compareResult = millionaire(s[0], s[x])
        print("result of user %d with user %d is %d" % (0, x, compareResult))

        if compareResult == -1:
            setR.append(s[x])
        elif compareResult == 0:
            setQ.append(s[x])
        else:
            setP.append(s[x])

    if len(setR) > 0:
        return findLeader(setR)
    if len(setQ) == 1:
        return (0, s[0], setP, setQ, setR)

    setV = []
    for user in s:
        if setQ.count(user) != 0:
            setV.append(user)
    return (1,s[0],setP,setQ,setR)

def millEncrypt(a,bob):
    a.mill_rand = str(random.getrandbits(233))
    a.save()
    return yynrsa.core.encrypt_int(int(a.mill_rand), int(bob.public_key), int(bob.rsa_n))

def millToBob(a,bob):
    return millEncrypt(a,bob) - a.rank

def millDecrypt(a,msg):
    return yynrsa.core.decrypt_int(msg,int(a.private_key),int(a.rsa_n))

def millCalMsgToA(b,pnl):
    notDone = True
    msgToA = []
    while notDone:
        notDone = False
        # print("fuck")
        (tpub,tpri) = yynrsa.newkeys(200)
        b.mill_prime = str(tpri.p)
        b.save()

        msgToA = [x%int(b.mill_prime) for x in pnl]

        for i in range(19):
            # print("msgToA[%d]: %d"%(i,msgToA[i]))
            if notDone:
                break
            for j in range(19):
                if i == j:
                    continue
                # print("msgToA[%d]: %d"%(j,msgToA[j]))
                if abs(msgToA[i] - msgToA[j]) < 3:
                    # print("fuck1")
                    notDone = True
                    break
            if msgToA[i] < 2:
                # print("fuck2")
                notDone = True
            if msgToA[i] > int(b.mill_prime) - 3:
                # print("fuck3")
                notDone = True
        # print("notDone: %d"%(notDone))
    # print("ahhhhhh")
    for i in range(19):
        if i < b.rank:
            msgToA[i] = msgToA[i] - 1
        elif i > b.rank:
            msgToA[i] = msgToA[i] + 1
    return msgToA

def millToAlice(b,msg):
    rankList = list(range(0,19))
    randList = [msg+x for x in rankList]
    possibleNumList = [millDecrypt(b,x) for x in randList]
    msgToA = millCalMsgToA(b,possibleNumList)
    return msgToA,int(b.mill_prime)

def millGetResult(a,msg,prime):
    remainder = int(a.mill_rand) % prime
    if remainder == msg[a.rank]:
        return 0
    elif remainder > msg[a.rank]:
        return 1
    else:
        return -1
    return -2

def millionaire(a,b):
    msgToB = millToBob(a,b)
    msgToA,primeOfB = millToAlice(b,msgToB)
    result = millGetResult(a,msgToA,primeOfB)
    return (0-result)

def voteLeader(cs, vs):
    (pub, pri) = yynrsa.newkeys(16)
    # la = int((pri.p-1)*(pri.q-1)/lcm((pri.p-1),(pri.q-1)))
    la = int((pri.p - 1) * (pri.q - 1))
    # al = 1
    # be = 1
    # g = ((al*pri.n+1)*pow(be,pri.n))%pow(pri.n,2)
    g = int(pri.n + 1)
    # mu = int(mod_inverse(L(pow(g,la) % pow(pri.n,2), pri.n), pri.n) % pri.n)
    mu = int(prime.mod_inverse(la, pri.n) % pri.n)
    # mu = L(pow(g,la) % pow(pri.n,2), pri.n) % pri.n

    nc = len(cs)
    nv = len(vs)
    base = nv + 2
    if base < 10:
        base = 10

    cList = []
    vList = []
    for c in cs:
        cList.append(c.id)
    for v in vs:
        for i in range(nc):
            if v.vote_to == cList[i]:
                vList.append(i)

    votes = []
    eMessage = 1
    tem = 0
    for i in range(nv):
        tm = int(pow(base, vList[i]))
        r = generate_big_prime(4)
        m = int(((pow(g, tm)) * (pow(r, pri.n))) % pow(pri.n, 2))
        votes.append(m)
        eMessage = (eMessage * m) % pow(pri.n, 2)
        tem = tem + tm
    # etem = int(((pow(g, tem)) * (pow(r, pri.n))) % pow(pri.n, 2))
    # detem = (L(pow(etem, la, pow(pri.n, 2)), pri.n) * mu) % pri.n

    dMessage = (L(pow(eMessage, la, pow(pri.n, 2)), pri.n) * mu) % pri.n
    results = []
    for i in range(nc):
        tr = dMessage % base
        results.append(tr)
        dMessage = (dMessage - tr) / base
    leaderIndex = results.index(max(results))
    return cs[leaderIndex]

def L(u,n):
    return (u-1)/n

def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = random.randint(1, num - 1)
        # print("val: %d, num: %d"%(val,num))
        if pow(val, num - 1, num) != 1:
            return False
    return True

def generate_big_prime(n):
    found_prime = False
    while not found_prime:
        p = random.randint(2 ** (n - 1), 2 ** n)
        if is_prime(p, 1000):
            return p

'''
### zyp test code
def get_cur_state(request):
    #print(request.POST['position_x'])
    #print(request.POST['position_y'])
    #i=random.randint(1,10)
    i=0
    return_dict={
        'player':'zypang',
        'position':[1,2],
        #'event':{
        #    'name':'vote_commander',
        #    'candidates':['junzhou','hainan'],
        #    'info':'vote for commander'
        #},
        #'can_choose_commander':1,
        'otherPlayers':
        {
            'junzhou':{'position':[3+i,5+i], 'known':0},
            'hainan':{'position':[5+i,11+i], 'known':1},
        },
    }
    return HttpResponse(json.dumps(return_dict))


def authenticate(request):
    return_dict={
        'success':0,
        'info':'hello \n world',
    }
    return HttpResponse(json.dumps(return_dict))

def chooseCommander(request):
    if request.POST['vote']=='1':
        return_dict={
            'success':1,
            'need_vote':0,
            'info':'choose commander success',
            'candidates':['junzhou','hainan'],
            'commander':request.POST['vote_commander']
        }
    else:
        return_dict={
            'success':0,
            'need_vote':1,
            'info':'there are 2 soldiers with same level, so we need to vote for commander',
            'candidates':['junzhou','hainan'],
            'commander':''
        }
    return HttpResponse(json.dumps(return_dict))

def open_house(request):
    return_dict={
        'success':1,
        'info':'open house success',
    }
    return HttpResponse(json.dumps(return_dict))

def game_over(request):
    pass
'''
