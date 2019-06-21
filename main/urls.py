from django.urls import path

from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('game/get_state/', views.get_cur_state, name='get_state'),
    path('game/init/', views.get_cur_state, name='init'),
    path('game/auth/', views.authenticate, name='auth'),
    path('game/commander/', views.chooseCommander, name='commander'),
    path('game/house/', views.open_house, name='open_house'),
    path('game/<slug:name>/', views.game, name='game'),
]
