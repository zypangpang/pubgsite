from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return render(request, 'main/index.html')


def game(request, name='firstGame'):
    return render(request, f'main/game.html', {"game_path": f"main/js/{name}.js"})
