from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views


app_name: str = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'password_change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        views.CustomPasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
]
