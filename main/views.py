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
    i=random.randint(1,10)
    return_dict={
        'player':'zypang',
        'position':[1,2],
        'event':'',
        'otherPlayers':
        {
            'junzhou':{'position':[3+i,5+i], 'known':0},
            'hainan':{'position':[5+i,11+i], 'known':1},
        },
    }
    return HttpResponse(json.dumps(return_dict))
