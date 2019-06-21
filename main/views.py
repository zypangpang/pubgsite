import json,random
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return render(request, 'main/index.html')


def game(request, name='firstGame'):
    return render(request, f'main/game.html', {"game_path": f"main/js/{name}.js"})


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
