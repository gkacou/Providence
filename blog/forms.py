from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q
from .models import (
    ProvUser,
    Cas,
    Reunion,
    Membre,
    NatureBesoin,
    AffectationNonLibere,
    Cotisation,
)


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

class AffectationNonLibereForm(ModelForm):
    """
    Formulaire utilisé pour les affectations de cas non libérés
    Filtre la liste des cotisations selon la réunion
    (formulaire inline)
    """
    class Meta:
        model = AffectationNonLibere
        fields = ('reunion', 'cotisation', 'collecteur', 'somme', 'cas')

    def __init__(self, *args, **kwargs):
        super(AffectationNonLibereForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['cotisation'].queryset = Cotisation.objects.filter(
                Q(social_libere=False) | Q(mission_libere=False),
                reunion=self.instance.reunion,
                # reunion__id=8,
            )

    # def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
    #     super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial, error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted, instance=instance, use_required_attribute=use_required_attribute, renderer=renderer)

class CotisationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.membre
