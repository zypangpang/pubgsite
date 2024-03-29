from django.urls import path

from . import views

app_name='main'

urlpatterns = [

    path('', views.choose_room, name='choose-room'),

    # 游戏主页面
    path('index', views.index, name='index'),

    # 游戏子页面
    path('game/get_state/', views.get_cur_state, name='get_state'),
    path('game/init/', views.get_cur_state, name='init'),
    path('game/auth/', views.authenticate, name='auth'),
    path('game/commander/', views.choose_cmd, name='commander'),
    path('game/house/', views.open_house, name='open_house'),
    path('game/gameover/', views.game_over, name='game_over'),
    path('game/<slug:name>/', views.game, name='game'),

    # 进入房间页面
    path('room', views.room, name='room'),

    # 进入房间页面
    path('choose_rank', views.choose_rank, name='choose_rank'),

    # 跳伞接口
    path('parachute', views.parachute, name='parachute'),

    # 数据初始化接口
    path('init', views.init, name='init'),

]
