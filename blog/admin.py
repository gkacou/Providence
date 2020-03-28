from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProvUser, Membre
# from .forms import ProvUserChangeForm


# Utilisateur Providence
@admin.register(ProvUser)
class ProvUserAdmin(UserAdmin):
    pass


# Membre Providence
@admin.register(Membre)
class ProvMembreAdmin(UserAdmin):
    model = Membre
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
            )}
        ),
    )
    radio_fields = {'sexe': admin.HORIZONTAL}
