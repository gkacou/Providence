from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import (
    ProvUser,
    Membre,
    FamilleCommunaute,
    Communaute,
    Reunion,
    Beneficiaire,
    NatureBesoin,
    Cas,
    Cotisation,
)

from .forms import CasCreationForm, CasChangeForm


# Utilisateur Providence
@admin.register(ProvUser)
class ProvUserAdmin(UserAdmin):
    pass


# Membre Providence
@admin.register(Membre)
class ProvMembreAdmin(UserAdmin):
    model = Membre
    list_display = ('last_name', 'first_name', 'telephone1', 'telephone2', 'adresse', 'email')
    list_display_links = ('last_name', 'first_name',)
    fieldsets = (
        ('Identification', {'fields': ('username', 'password')}),
        ('Informations personnelles',
            {'fields': (
                ('last_name', 'first_name',),
                'email',
                'sexe',
                'date_naissance',
                ('telephone1', 'telephone2',),
                'adresse',
                'date_adhesion',
                'communaute',
                ('activite', 'profession',),
                ('cotisation_social', 'cotisation_mission',),
                'personne_physique',
            )}
        ),
    )
    radio_fields = {'sexe': admin.HORIZONTAL}

    # def get_queryset(self, *args, **kwargs):
    #     return Membre.objects.filter(is_superuser=False)


# Familles d'églises et églises
@admin.register(FamilleCommunaute)
class FamilleCommunauteAdmin(admin.ModelAdmin):
    pass

@admin.register(Communaute)
class CommunauteAdmin(admin.ModelAdmin):
    pass


# Bénéficiaire
@admin.register(Beneficiaire)
class BeneficiaireAdmin(admin.ModelAdmin):
    pass


# Cas
@admin.register(Cas)
class CasAdmin(admin.ModelAdmin):
    form = CasChangeForm
    add_form = CasCreationForm
    add_fieldsets = (
        (None, {
            'fields': (
                'soumis_par',
                'reunion',
                'beneficiaire',
                'classification',
                'urgence',
            )
        }),
    )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def get_changeform_initial_data(self, request):
        reunion = Reunion.objects.all()[0]  # Réunion la plus récente
        return {
            'soumis_par': request.user,
            'reunion' : reunion,
        }

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return ('classification',)
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Utiliser un formulaire différent lors de la création
        """
        defaults = {}
        if obj is None:   # Si l'objet n'existe pas encore
            defaults['form'] = self.add_form

        defaults.update(kwargs)  # Transférer les autres paramètres dans defaults
        return super().get_form(request, obj, **defaults)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Détermine la classe HttpResponse pour l'étape add_view.
        Il est personnalisé car la création des cas suit
        une logique similaire à celle de la création des utilisateurs
        """
        # Il faut permettre la poursuite de la modification du cas qui vient
        # d'être créé, donc le bouton 'Enregistrer' doit se comporter comme
        # le boutton 'Enregistrer et poursuivre la modif' sauf si :
        # * L'utilisateur a cliqué sur 'Enregistrer et ajouter un autre'
        # * Nous ajoutons un cas depuis un popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)



# Nature de besoin
@admin.register(NatureBesoin)
class NatureBesoinAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'classification')

# Réunion
@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    pass
