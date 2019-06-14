from django.urls import path

from . import views
app_name='account'
urlpatterns = [
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('useradmin/', views.user_manage, name='useradmin'),
    path('useradmin/adduser/', views.add_user, name='adduser'),
    path('useradmin/deluser/', views.del_user, name='deluser'),
    path('useradmin/initgroup/', views.init_group, name='initgroup'),
    path('useradmin/changepwd/', views.change_pwd, name='changepwd'),
    path('useradmin/changegroup/', views.change_group, name='changegroup'),
]
