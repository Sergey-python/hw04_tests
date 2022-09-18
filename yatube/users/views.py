from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordChangeDoneView)
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    template_name = 'users/signup.html'
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
