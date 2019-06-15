from django.urls import path

from . import views

app_name='main'
urlpatterns = [
    # 选择房间页面及接口
    path('', views.choose_room, name='choose-room'),

    # 游戏主页面
    path('index', views.index, name='index'),

    # 游戏子页面
    path('game/<slug:name>/', views.game, name='game'),

    # 进入房间页面
    path('room', views.room, name='room'),

    # 跳伞接口
    path('parachute', views.parachute, name='parachute'),

    # 人物移动接口
    path('move', views.move, name='move'),

    # 认证接口
    path('certificate', views.certificate, name='certificate'),

    # 选择指挥官接口
    path('choose-commander', views.choose_cmd, name='choose-commander'),

    # 开箱子接口
    path('open-box', views.open_box, name='open-box'),

    # 数据初始化接口
    path('init', views.init, name='init'),

]
