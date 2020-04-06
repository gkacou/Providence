from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ProvUser, Cas, Reunion, Membre, NatureBesoin


class ProvUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = ProvUser
        fields = ('username', 'email')


class CasCreationForm(ModelForm):
    """
    Formulaire utilisé lors de la création initiale d'un Cas
    """
    soumis_par = forms.ModelChoiceField(
        queryset=Membre.objects.filter(personne_physique=True)
    )
    reunion = forms.ModelChoiceField(
        queryset=Reunion.objects.all(),
        # widget=forms.TextInput,
        disabled=False,
    )

    class Meta:
        model = Cas
        fields = (
            'soumis_par',
            'reunion',
            'beneficiaire',
            'classification',
            'urgence',
        )

class CasChangeForm(ModelForm):
    """
    Formulaire utilisé pour la modification d'un Cas
    """
    def __init__(self, *args, **kwargs):
        super(CasChangeForm, self).__init__(*args, **kwargs)
        self.fields['nature'].queryset = NatureBesoin.objects.filter(
            classification=self.instance.classification,
        )
    # class Meta:
    #     model = Cas
    #     fields = ('',)
