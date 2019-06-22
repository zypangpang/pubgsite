from django.shortcuts import render

import csv, bisect, json, logging, random
import rsa as yynrsa
from django.conf import settings
from django.contrib.auth.models import User, Group
# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.http import HttpResponse, Http404

from main import models, prime

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
    return redirect('main:choose-room')

@login_required
def choose_rank(request):
    rank = request.GET['rank']
    user_id = request.user.id
    if user_id < 1 or user_id > 19:
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
    user_id = request.user.id
    user = models.User.objects.get(id=user_id)
    all_users = models.User.objects.filter(group_id=user.group_id)

    if request.POST['vote'] == '1':
        authName = request.POST['vote_commander']
        authVC = User.objects.get(username=authName)
        user.vote_to = authVC.id
        user.save()

        cs = []
        okFlag = 1
        for u in all_users:
            if u.vote_to is None:
                okFlag = 0
                break
            else:
                cs.append(models.Users.objects.get(id=u.vote_to))

        if okFlag == 0:
            return_dict = {
                'success': 0,
                'need_vote': 1,
                'info': 'choosing commander\nplease wait',
                'candidates': [],
                'commander': ''
            }
        else:
            commander = voteLeader(cs,all_users)
            authCom = User.objects.get(id=commander.id)
            info = 'commander is ' + authCom.username
            return_dict = {
                'success': 1,
                'need_vote': 0,
                'info': info,
                'candidates': [authCom.username],
                'commander': authCom.username
            }
    else:
        (tempResult,commander,setP,setQ,setR) = findLeader(all_users)
        if tempResult == 0:
            authCom = User.objects.get(id=commander.id)
            info = 'commander is '+authCom.username
            return_dict = {
                'success': 1,
                'need_vote': 0,
                'info': info,
                'candidates': [authCom.username],
                'commander': authCom.username
            }
        else:
            can = []
            for u in setQ:
                tempAU = User.objects.get(id=u.id)
                can.append(tempAU.username)
            return_dict = {
                'success': 0,
                'need_vote': 1,
                'info': 'there are soldiers with same rank, so we need to vote for commander',
                'candidates': can,
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

def findLeader(s):
    setP = []
    setQ = []
    setR = []
    n = len(s)
    if n == 1:
        return (0,s[0],setP,setQ,setR)
    # print("millionaire begin")
    for x in range(n):
        if x == 0:
            setQ.append(s[0])
            continue
        # print("comparing %d of rank %d and %d of rank %d "%(0,s[0].rank,x,s[x].rank))
        compareResult = millionaire(s[0],s[x])
        # print("result of user %d with user %d is %d"%(0,x,compareResult))
        if compareResult == 1:
            setR.append(s[x])
        elif compareResult == 0:
            setQ.append(s[x])
        else:
            setP.append(s[x])

    if len(setR) > 0:
        return findLeader(setR)
    if len(setQ) == 1:
        return (0,s[0],setP,setQ,setR)

    setV = []
    for user in s:
        if setQ.count(user) != 0:
            setV.append(user)
    return (1,s[0],setP,setQ,setR)

def millionaire(a,b):
    msgToB = millToBob(a,b)
    msgToA,primeOfB = millToAlice(b,msgToB)
    result = millGetResult(a,msgToA,primeOfB)
    return result

def millToBob(a, bob):
    return millEncrypt(a,bob) - a.rank

def millEncrypt(a, bob):
    a.mill_rand = random.getrandbits(233)
    return yynrsa.core.encrypt_int(a.mill_rand, bob.__private_key.e, bob.__private_key.n)

def millDecrypt(a, msg):
    return yynrsa.core.decrypt_int(msg, a.__private_key.d, a.__private_key.n)

def millToAlice(b, msg):
    rankList = list(range(1, 20))
    randList = [msg + x for x in rankList]
    possibleNumList = []
    for x in randList:
        possibleNumList.append(millDecrypt(b,x))
    # possibleNumList = [self.millDecrypt(x) for x in randList]
    msgToA = millCalMsgToA(b,possibleNumList)
    return msgToA, b.mill_prime

def genMillRand(n):
    (tpub, tpri) = yynrsa.newkeys(n)
    return tpri.p

def millCalMsgToA(b, pnl):
    notDone = True
    msgToA = []
    while notDone:
        notDone = False
        (tpub, tpri) = yynrsa.newkeys(200)
        b.mill_prime = tpri.p
        msgToA = [x % b.mill_prime for x in pnl]
        for i in range(19):
            if notDone:
                break
            for j in range(19):
                if i == j:
                    continue
                if abs(msgToA[i] - msgToA[j]) < 3:
                    notDone = True
                    break
            if msgToA[i] < 2:
                notDone = True
            if msgToA[i] > b.mill_prime - 3:
                notDone = True
    for i in range(19):
        if i < b.rank:
            msgToA[i] = msgToA[i] - 1
        elif i > b.rank:
            msgToA[i] = msgToA[i] + 1
    return msgToA

def millGetResult(a, msg, prime):
    remainder = a.mill_rand % prime
    if remainder == msg[a.rank]:
        return 0
    elif remainder > msg[a.rank]:
        return 1
    else:
        return -1
    return -2

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
