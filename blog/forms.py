import locale
from sys import platform
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
    """
    Pour afficher le nom du membre dans la liste déroulante
    de sélection de la cotisation dans le formulaire d'affectation
    des montants non libérés
    """
    def label_from_instance(self, obj):
        return obj.membre


class CasChoiceField(forms.ModelChoiceField):
    """
    Pour afficher dans la liste déroulante de sélection du cas:
    - le nom du bénéficiaire
    - la classification du cas : 'S' ou 'M4
    - le montant alloué
    """
    def label_from_instance(self, obj):
        # Affecter une localisation si nécessaire
        if not bool(locale.getlocale()[0]):
            if platform == "linux" or platform == "linux2":
                locale.setlocale(locale.LC_ALL, 'fr_FR')
            elif platform == "darwin":
                locale.setlocale(locale.LC_ALL, 'fr_FR')
            elif platform == "win32":
                locale.setlocale(locale.LC_ALL, 'French_France.1252')
        montant = f'{obj.montant_alloue:n}'
        return f'{obj.beneficiaire} ({obj.classification} : {montant})'

