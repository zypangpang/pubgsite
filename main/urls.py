from django.urls import path

from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('game/get_state/', views.get_cur_state, name='get_state'),
    path('game/<slug:name>/', views.game, name='game'),
]
