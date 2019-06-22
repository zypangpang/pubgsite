import json,random
from django.shortcuts import render
from django.contrib.auth.models import User
import models
import rsa
import lagrange

from django.http import HttpResponse

# 接口
@login_required
def index(request):
    return render(request, 'main/index.html')


@login_required
def game(request, name='firstGame'):
    return render(request, f'main/game.html', {"game_path": f"main/js/{name}.js"})

def init(request):
    #TODO: waiting for gaoming to complete this
    pass

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
        else if u.group_id == user.group_id:
            same_group = 1
            known_count += 1
        other_players[u.user_id] = {'position': [u.position_x, u.position_y],
                                    'known': same_group}

    if (known_count >= 4) && (global_status.intValue <= 1):
        global_status.intValue = 2
        global_status.save()

    return_dict={
        'player': username,
        'position': [user.position_x, user.position_y],
        'can_choose_commander': 1 if global_status.intValue == 2 else 0,
        'otherPlayers': other_players
    }

    if(u.certificating_with > 0):
        c_username = User.objects.get(id=u.certificating_with).get_username()
        return_dict['event'] = {'name': 'auth',
                                'username': c_username,
                                'info': 'you are certificating with ' + c_username + '.'}
    if(u.opening_box > 0):
        return_dict['event'] = {'name': 'open_house',
                                'house_id': u.opening_box,
                                'info': 'you are opening box ' + str(u.opening_box) + '.'}

    global_status = models.SystemParam.objects.get(key='global_status').intValue
    #TODO: fetch candidates list
    if global_status == 3:
        if user.vote_to <= 0:
            candidates = ['junzhou','hainan']
            return_dict['event'] = {'name': 'vote_commander',
                                    'candidates': candidates,
                                    'info': 'vote for commander. options: ' + ', '.join(candidates) + '.'}
    else if global_status == 5:
        return_dict['event'] = {'name': 'game_over',
                                'end': 1,
                                'info': 'you enter the house and find lot\'s of shinning weapons.'}
    else if global_status == 6:
        return_dict['event'] = {'name': 'game_over',
                                'end': 1,
                                'info': 'you enter the house. suddenly the house explode. you die.'}

    return HttpResponse(json.dumps(return_dict))


def authenticate(request):
    '''
        certificate_result: 1 success, 0 fail
    '''
    from_id = request.user.id
    user = models.Users.objects.get(user_id=request.user.id)
    to_id = request.POST['to_id']

    user.certificating_with = to_id
    user.save()

    result = rsa.two_way_certificate(from_id, to_id)
    info = ""
    if result == 1:
        rsa.merge_user_group(from_id, to_id)
        info = "certificate with user " + str(to_id) + " succeed."
    else:
        info = "certificate with user " + str(to_id) + " fail."
    return_dict = {'success': result,
                   'info': info}

    user.certificating_with = -1
    user.save()
    return HttpResponse(json.dumps(return_dict))

def open_house(request):
    user_id = request.user.id
    user = models.Users.objects.get(user_id=request.user.id)
    position = (user.position_x, user.position_y)
    box_id = -1

    '''
    house 1: (3,21-24)(4-6,22-24)
    house 2: (20,3-6)(21-23,4-6)
    '''
    house_range = []
    house_range.append([(2,y) for y in range(20,26)] + [(x,25) for x in range(3,8)] +
                       [(7,y) for y in range(21,25)] + [(x,21) for x in range(4,7)] +
                       [(3,20), (4,20)])
    house_range.append([(19,y) for y in range(2,8)] + [(x,7) for x in range(20,25)] +
                       [(24,y) for y in range(3,7)] + [(x,3) for x in range(21,24)] +
                       [(20,2), (21,2)])
    for i in range(len(house_range)):
        if position in house_range[i]:
            box_id = i
            break

    if box_id < 0:
        return_dict = {'success': 0,
                       'info': 'you are not close to any house.'}
        return HttpResponse(json.dumps(return_dict))

    user.opening_box = box_id
    user.save()

    user_list = models.Users.objects.all()
    key_list = []
    for u in user_list:
        if u.group_id == user.group_id:
            if (u.position_x, u.position_y) in house_range[box_id]:
                key_list.append((u.box_key_x, u.box_key_y))

    solve_result = lagrange.solve_lagrange(key_list, box.least_num)
    result = 0
    info = "open fail"
    if solve_result == -1:
        result = 0
        info = "need more people to open the box"
    else if solve_result == -2:
        result = 0
        info = "the key is conflict"
    else if solve_result == box.password:
        result = 1
        info = "open succeed"

    return_dict = {'success': result,
                   'info': info}
    user.opening_box = -1
    user.save()
    return HttpResponse(json.dumps(return_dict))

def game_over(request):
    ending = request.POST['ending']
    global_status = models.SystemParam.objects.get(key='global_status')
    if ending == 1:
        global_status.intValue = 5
    else if ending == 0:
        global_status.intValue = 6
    global_status.save()
