from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ProvUser


class ProvUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = ProvUser
        fields = ('username', 'email')
